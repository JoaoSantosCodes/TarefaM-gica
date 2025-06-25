import os
import shutil

# Definições de organização
SCRIPTS = [
    'app.py', 'build_apk_final.py', 'build_with_android_studio.py', 'build_with_temp_dir.py',
    'create_minimal_apk.py', 'final_setup.py', 'fix_avd.py', 'fix_gradle_and_build.py',
    'fix_gradle_complete.bat', 'fix_gradle_permissions_and_cleanup.py', 'fix_gradle_permissions.ps1',
    'install_android_sdk_complete.py', 'install_android_sdk_simple.py', 'install_apk_automated.py',
    'open_android_studio.py', 'quick_validate.py', 'run_security_tests.py', 'run_validation_tests.py',
    'security_fixes.py', 'setup_android_build.py', 'setup_android_emulator.py', 'setup_android_simple.py',
    'setup_complete_environment_simple.py', 'setup_complete_environment.py', 'setup_emulator_simple.py',
    'start_emulator_robust.py', 'start_emulator_simple.bat', 'start_emulator_simple.py', 'temp_audit_fix.py',
    'test_audit_simple.py', 'test_automated_suite.py', 'test_pix_integration.py', 'test_rate_limit_server.py',
    'test_rate_limiting_fix.py', 'validate_build_environment.py'
]

BUILD = [
    'build_apk_automated.bat', 'download_java17.ps1', 'setup_java17.ps1', 'download_gradle_wrapper.py'
]

# Pastas a serem criadas
FOLDERS = ['scripts', 'build', 'outputs']

# Pastas a serem movidas para outputs
OUTPUTS_FOLDERS = ['logs', 'test_reports']

# Função para mover arquivos

def move_file(file, dest_folder):
    if os.path.exists(file):
        os.makedirs(dest_folder, exist_ok=True)
        shutil.move(file, os.path.join(dest_folder, os.path.basename(file)))
        print(f"Movido: {file} -> {dest_folder}/")

def move_folder(folder, dest_folder):
    if os.path.exists(folder):
        os.makedirs(dest_folder, exist_ok=True)
        shutil.move(folder, os.path.join(dest_folder, os.path.basename(folder)))
        print(f"Movido: {folder} -> {dest_folder}/")

if __name__ == "__main__":
    # Cria as pastas principais
    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)

    # Move scripts
    for script in SCRIPTS:
        move_file(script, 'scripts')

    # Move arquivos de build
    for build_file in BUILD:
        move_file(build_file, 'build')

    # Move pastas de saída
    for out_folder in OUTPUTS_FOLDERS:
        move_folder(out_folder, 'outputs')

    print("Organização automática concluída!") 