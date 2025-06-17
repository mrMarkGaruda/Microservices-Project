@echo off
setlocal enableextensions enabledelayedexpansion
set BASE_URL=http://localhost:5000
set BILLING_URL=http://localhost:5003
set COACH_URL=http://localhost:5001
set MONOLITH_URL=http://localhost:5004
set STATS_URL=http://localhost:5002

curl -X POST %MONOLITH_URL%/users -H "Content-Type: application/json" -d "{\"email\":\"jane.doe@mail.com\",\"name\":\"Jane Doe\",\"role\":\"user\"}"
echo.
curl %BILLING_URL%/billing/plans
echo.
curl -X POST %BILLING_URL%/billing/subscriptions -H "Content-Type: application/json" -d "{\"user_email\":\"jane.doe@mail.com\",\"plan_id_name\":\"premium_monthly\"}"
echo.
curl %BILLING_URL%/billing/subscriptions/users/jane.doe@mail.com
echo.
curl -X POST %COACH_URL%/createWod -H "Content-Type: application/json" -d "{\"user_email\":\"jane.doe@mail.com\"}"
echo.
curl -X POST %MONOLITH_URL%/workouts/register -H "Content-Type: application/json" -d "{\"email\":\"jane.doe@mail.com\",\"exercises\":[1,2,3,4,5,6,7,8,9]}"
echo.
curl -X POST %MONOLITH_URL%/workouts/1/perform
echo.
curl %STATS_URL%/stats/users/jane.doe@mail.com
echo.
curl -X POST %COACH_URL%/subscription/cancel -H "Content-Type: application/json" -d "{\"user_email\":\"jane.doe@mail.com\"}"
echo.
curl %BILLING_URL%/billing/subscriptions/users/jane.doe@mail.com
echo.
endlocal
