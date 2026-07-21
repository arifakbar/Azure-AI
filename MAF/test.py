import pkgutil

for _, name, _ in pkgutil.walk_packages():
    if "openapi" in name.lower():
        print(name)