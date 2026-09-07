# mj-native

## VPS (pehle yeh)

```bash
cd jarvis-assistant
pip install -r requirements.txt
export MJ_API_KEY=change-me
uvicorn api_server:app --host 0.0.0.0 --port 8080
```

Phone use ho to `mj-native/.env` mein IP:

```
EXPO_PUBLIC_MJ_API_URL=http://YOUR_VPS_IP:8080
EXPO_PUBLIC_MJ_API_KEY=change-me
```

API key dono jagah same.

## Sirf yeh command (app)

```bash
cd mj-native
npm install
npx expo start
```

App khulte hi `/health` call karti hai. Settings tab optional hai.
