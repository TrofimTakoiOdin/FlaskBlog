import subprocess


def install_dependencies():
    # Install Python packages from requirements.txt
    subprocess.run(['pip', 'install', '-r', 'requirements.txt'])


def main():
    print("Installing Flask Blog App...")
    install_dependencies()
    print("App installation completed.")


if __name__ == "__main__":
    main()
