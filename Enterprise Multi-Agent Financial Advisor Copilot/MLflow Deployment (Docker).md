apiVersion: apps/v1
kind: Deployment

metadata:
  name: mlflow

spec:

  replicas: 1

  template:

    spec:

      containers:

        - name: mlflow

          image: ghcr.io/mlflow/mlflow

          ports:
            - containerPort: 5000

          command:
            - mlflow
            - server
            - --host
            - 0.0.0.0