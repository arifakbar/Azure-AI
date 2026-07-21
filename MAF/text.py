import agent_framework
import agent_framework.azure as azure_mod
print("agent_framework version:", getattr(agent_framework, "__version__", "unknown"))
print("Available symbols:")
print(dir(azure_mod))