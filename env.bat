@echo off
REM Quick fix for MedGPT environment issues

echo ========================================
echo MedGPT Environment Fix Script
echo ========================================
echo.

REM Step 1: Clear old environment variable
echo [1/4] Clearing old GROQ_API_KEY...
set GROQ_API_KEY=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
echo Done.
echo.

REM Step 2: Delete old .env file (if corrupted)
echo [2/4] Removing corrupted .env file...
if exist .env (
    del .env
    echo Deleted old .env
) else (
    echo No .env file found
)
echo.

REM Step 3: Create new .env file with UTF-8 encoding
echo [3/4] Creating new .env file...
echo # MedGPT Environment Variables > .env
echo # Add your Groq API key below: >> .env
echo GROQ_API_KEY=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 >> .env
echo.
echo Created new .env file.
echo IMPORTANT: Edit .env and replace 'your_key_here' with your actual Groq API key!
echo.

REM Step 4: Test
echo [4/4] Current directory:
cd
echo.

echo ========================================
echo Fix Complete!
echo ========================================
echo.
echo NEXT STEPS:
echo 1. Open .env file in Notepad
echo 2. Replace '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' with your actual Groq API key
echo 3. Save the file
echo 4. Run: python test_groq.py
echo.
pause