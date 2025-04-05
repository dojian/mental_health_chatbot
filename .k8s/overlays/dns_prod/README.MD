# DNS Prod

##  Setup



## Troubleshooting commands
```bash
kubectl get certificate -n istio-system
kubectl describe certificate genzen-cert -n istio-system

kubectl get secret genzen-info-tls -n istio-system

kubectl get gateway frontend-gateway -n istio-system -o yaml

kubectl get service istio-ingressgateway -n istio-system -o yaml

curl -v https://genzen.info
curl -v --insecure https://genzen.info

nslookup genzen.info


kubectl logs -n istio-system -l app=istio-ingressgateway

kubectl rollout restart deployment istio-ingressgateway -n istio-system



```

https://github.com/aws-samples/eks-alb-istio-with-tls/blob/main/istio/yelb-services.yaml