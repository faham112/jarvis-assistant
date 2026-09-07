# mj-native

Expo React Native UI for MJ.

## API (VPS)

```bash
pip install -r requirements.txt
export MJ_API_KEY='ek-lamba-secret'
uvicorn api_server:app --host 0.0.0.0 --port 8080
```

```bash
curl -H "X-API-Key: ek-lamba-secret" http://127.0.0.1:8080/health
```

## App

```bash
cd mj-native
npm install
npx expo start
```

Expo Go se scan. Settings: `http://VPS_IP:8080` + same key.

Android emulator: `http://10.0.2.2:8080`
