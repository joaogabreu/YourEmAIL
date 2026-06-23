set -euo pipefail

EKS_CLUSTER="${EKS_CLUSTER:-youremail-homolog}"
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:?AWS_ACCOUNT_ID obrigatorio}"

aws eks update-kubeconfig --name "$EKS_CLUSTER" --region "$AWS_REGION" >/dev/null

if ! command -v helm >/dev/null 2>&1; then
  curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
fi

OIDC_ISSUER="$(aws eks describe-cluster --name "$EKS_CLUSTER" --region "$AWS_REGION" \
  --query cluster.identity.oidc.issuer --output text)"
OIDC_HOST="${OIDC_ISSUER#https://}"
ROLE_NAME="${EKS_CLUSTER}-alb-controller"
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/AWSLoadBalancerControllerIAMPolicy"

if ! aws iam list-open-id-connect-providers \
  --query "OpenIDConnectProviderList[?contains(Arn, '${OIDC_HOST}')]" --output text | grep -q .; then
  aws iam create-open-id-connect-provider \
    --url "$OIDC_ISSUER" \
    --client-id-list sts.amazonaws.com \
    --thumbprint-list 9e99a48a9960b14926bb7f3b02e22da2b0ab7280
fi

if ! aws iam get-policy --policy-arn "$POLICY_ARN" >/dev/null 2>&1; then
  curl -fsSL -o /tmp/iam_policy.json \
    https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.11.0/docs/install/iam_policy.json
  aws iam create-policy --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file:///tmp/iam_policy.json
fi

if ! aws iam get-role --role-name "$ROLE_NAME" >/dev/null 2>&1; then
  cat > /tmp/trust.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_HOST}" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "${OIDC_HOST}:sub": "system:serviceaccount:kube-system:aws-load-balancer-controller",
        "${OIDC_HOST}:aud": "sts.amazonaws.com"
      }
    }
  }]
}
EOF
  aws iam create-role --role-name "$ROLE_NAME" --assume-role-policy-document file:///tmp/trust.json
  aws iam attach-role-policy --role-name "$ROLE_NAME" --policy-arn "$POLICY_ARN"
fi

kubectl apply -f - <<EOF
apiVersion: v1
kind: ServiceAccount
metadata:
  name: aws-load-balancer-controller
  namespace: kube-system
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::${AWS_ACCOUNT_ID}:role/${ROLE_NAME}
EOF

VPC_ID="$(aws eks describe-cluster --name "$EKS_CLUSTER" --region "$AWS_REGION" \
  --query cluster.resourcesVpcConfig.vpcId --output text)"

helm repo add eks https://aws.github.io/eks-charts 2>/dev/null || true
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/ 2>/dev/null || true
helm repo update

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName="$EKS_CLUSTER" \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller \
  --set region="$AWS_REGION" \
  --set vpcId="$VPC_ID"

helm upgrade --install metrics-server metrics-server/metrics-server \
  -n kube-system \
  --set args[0]=--kubelet-insecure-tls

kubectl wait --for=condition=available deployment/aws-load-balancer-controller \
  -n kube-system --timeout=300s
kubectl rollout status deployment/metrics-server -n kube-system --timeout=300s
