import re
import pkgutil
import subprocess


uninstalled_packages = []
# 获取 requirements.txt 中的包名列表
with open("requirements.txt") as f:
    required_packages = []
    for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        package_name = re.match(r'^\s*[\w\-]+(?:[\s\[\]\(\)\w\d\.\\/@-]+\s*[\w\d])?', line)
        if package_name:
            required_packages.append(package_name.group().split()[0])
            try:
                subprocess.check_output(['pip', 'show', required_packages[-1]])
            except subprocess.CalledProcessError:
                uninstalled_packages.append(required_packages[-1])


# 将未安装的包名重新组织成新的requirements.txt文件
with open('uninstalled_requirements.txt', 'w') as f:
    for package in uninstalled_packages:
        f.write(f"{package}\n")