import { defineRailway, postgres, preserve, project, service } from "railway/iac";

export default defineRailway(() => {
  const postgresDatabase = postgres("postgres");
  const pythonApp = service("python-app", {
    replicas: 1,
    env: {
      DATABASE_URL: preserve(),
    },
  });

  return project("deploy-strategies-python-app", {
    resources: [postgresDatabase, pythonApp],
  });
});
