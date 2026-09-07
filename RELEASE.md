# MJ Android Releases

GitHub Actions automatically builds and publishes the Android APK when a version tag is pushed.

## One-time setup

Add an Actions secret in the repository:

- Name: `EXPO_TOKEN`
- Value: Expo/EAS access token for the `faham112` account

## Publish a release

From the repository:

```bash
git pull --ff-only origin main
git tag v1.0.1
git push origin v1.0.1
```

The workflow builds the `mj-native` Expo preview APK through EAS and attaches it to a GitHub Release. Download it from the repository's **Releases** page.

You can also run **Actions -> MJ Android Release -> Run workflow** and provide a tag such as `v1.0.2`.
