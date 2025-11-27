@echo off
echo ============================================
echo   Création des dossiers et fichiers manquants
echo ============================================

REM Racine
mkdir assets\defaults
mkdir games\demo
mkdir games\demo\npcs
mkdir games\demo\saves

mkdir src\common
mkdir src\engine
mkdir src\engine\ai
mkdir src\engine\net
mkdir src\engine\ui
mkdir src\editor
mkdir src\editor\graph
mkdir src\editor\panels
mkdir src\tools

REM === Création fichiers communs ===
call :create_file "src\common\rpg_models.py"
call :create_file "src\common\game_enums.py"
call :create_file "src\common\loaders.py"

REM === Fichiers Engine ===
call :create_file "src\engine\inventory.py"
call :create_file "src\engine\loot.py"
call :create_file "src\engine\quests.py"
call :create_file "src\engine\world.py"
call :create_file "src\engine\travel.py"
call :create_file "src\engine\npcs.py"
call :create_file "src\engine\encounters.py"

call :create_file "src\engine\ai\client.py"
call :create_file "src\engine\ai\prompts.py"

call :create_file "src\engine\net\api_server.py"

REM === UI Engine ===
REM (pas de fichiers obligatoires, ils existent déjà normalement)

REM === Éditeur ===
call :create_file "src\editor\project_manager.py"
call :create_file "src\editor\graph\node_types.py"

REM === Panneaux Éditeur ===
call :create_file "src\editor\panels\item_editor.py"
call :create_file "src\editor\panels\quest_editor.py"
call :create_file "src\editor\panels\npc_editor.py"
call :create_file "src\editor\panels\world_editor.py"
call :create_file "src\editor\panels\playtest_panel.py"

REM === Tools ===
call :create_file "src\tools\import_from_twine.py"
call :create_file "src\tools\validate_project.py"

REM === Jeux ===
call :create_file "games\demo\story.json"
call :create_file "games\demo\world.json"
call :create_file "games\demo\items.json"

echo.
echo ============================================
echo   Création terminée !
echo ============================================
pause
exit /b


:create_file
REM %1 = fichier
if exist %1 (
    echo [EXISTE] %1
) else (
    echo. > %1
    echo [CREATED] %1
)
exit /b
