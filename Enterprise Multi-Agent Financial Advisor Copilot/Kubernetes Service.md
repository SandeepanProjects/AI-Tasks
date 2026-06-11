apiVersion: v1
kind: Service

metadata:
  name: advisor-api-service

spec:

  selector:
    app: advisor-api

  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000

  type: LoadBalancer