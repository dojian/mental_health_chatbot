# DNS Prod

##  Setup
1. install eks: `eksctl create cluster -f eksctl-cluster-config.yaml`
1. update eks IAM policy for route53
1. remove route53 a records and create new a records for genzen.info and www.genzen.info
  1. attach the elb to the route53 hosted zone
1. Update RDS with the correct eks vpc else it will brick...
1. install istio: `istioctl install --set profile=demo -y`
2. install cert-manager: `kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.17.0/cert-manager.yaml`
1. install prometheus: `kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/addons/prometheus.yaml`
1. install grafana: `kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/addons/grafana.yaml`
1. install kiali: `kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/addons/kiali.yaml`
1. install jaeger: `kubectl apply -f https://raw.githubusercontent.com/istio/istio/release-1.25/samples/addons/jaeger.yaml`
3. set up certificates and gateway: `k apply -k .k8s/overlays/dns_prod/setup`
4. ensure RDS is running.
5. run kustomize: `k apply -k .k8s/overlays/dns_prod`


### Observability
```bash
kubectl get pods -n istio-system
istioctl dashboard prometheus # This opens Prometheus at http://localhost:9090 where you can query Istio metrics
istioctl dashboard grafana # This provides access to pre-built Istio dashboards at http://localhost:3000
istioctl dashboard kiali # Kiali provides a topology view of your services, health status, and allows you to manage Istio configurations

```

## Troubleshooting commands
```bash
kubectl get certificate -n istio-system
kubectl describe certificate genzen-cert -n istio-system

kubectl get secret genzen-info-tls -n istio-system

kubectl describe certificaterequest genzen-cert-1 -n istio-system

kubectl logs -n cert-manager -l app=cert-manager

kubectl get gateway frontend-gateway -n istio-system -o yaml

kubectl get service istio-ingressgateway -n istio-system -o yaml

curl -v https://genzen.info
curl -v --insecure https://genzen.info

nslookup genzen.info


kubectl logs -n istio-system -l app=istio-ingressgateway

kubectl rollout restart deployment istio-ingressgateway -n istio-system



```

https://github.com/aws-samples/eks-alb-istio-with-tls/blob/main/istio/yelb-services.yaml
https://www.youtube.com/watch?v=rbFuEHtXPNs
