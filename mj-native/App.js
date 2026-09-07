import { useEffect, useRef, useState } from "react";
import {
  SafeAreaView, View, Text, TextInput, TouchableOpacity, FlatList,
  StyleSheet, KeyboardAvoidingView, Platform, StatusBar,
} from "react-native";
import AsyncStorage from "@react-native-async-storage/async-storage";
import { ping, sendChat } from "./src/api";
import { DEFAULT_URL, DEFAULT_KEY } from "./src/config";

const QUICK = [
  { label: "Time", text: "time" },
  { label: "Health", text: "system health" },
  { label: "Notes", text: "read notes" },
  { label: "Joke", text: "joke" },
];

export default function App() {
  const [tab, setTab] = useState("chat");
  const [baseUrl, setBaseUrl] = useState(DEFAULT_URL);
  const [apiKey, setApiKey] = useState(DEFAULT_KEY);
  const [status, setStatus] = useState("offline");
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [messages, setMessages] = useState([
    { id: "0", role: "mj", text: "Connecting to MJ API..." },
  ]);
  const list = useRef(null);

  useEffect(() => {
    let alive = true;
    (async () => {
      const u = (await AsyncStorage.getItem("mj_url")) || DEFAULT_URL;
      const k = (await AsyncStorage.getItem("mj_key")) || DEFAULT_KEY;
      if (!alive) return;
      setBaseUrl(u);
      setApiKey(k);
      try {
        const h = await ping({ baseUrl: u, apiKey: k });
        if (!alive) return;
        setStatus(h.ok ? "online" : "error");
        setMessages((m) => m.concat([{
          id: "boot",
          role: "mj",
          text: h.ok ? "API connected. Ollama: " + (h.ollama ? "yes" : "no") : "Health fail",
        }]));
      } catch (e) {
        if (!alive) return;
        setStatus("error");
        setMessages((m) => m.concat([{
          id: "boot-err",
          role: "mj",
          text: "API connect nahi: " + e.message + ". uvicorn chalao. Phone ho to .env mein VPS IP.",
        }]));
      }
    })();
    return () => { alive = false; };
  }, []);

  const push = (role, text) => {
    setMessages((m) => m.concat([{ id: String(Date.now()) + role, role, text }]));
  };

  const saveSettings = async () => {
    await AsyncStorage.setItem("mj_url", baseUrl.trim());
    await AsyncStorage.setItem("mj_key", apiKey.trim());
    try {
      const h = await ping({ baseUrl: baseUrl.trim(), apiKey: apiKey.trim() });
      setStatus(h.ok ? "online" : "error");
      push("mj", h.ok ? "Connected" : "Health fail");
    } catch (e) {
      setStatus("error");
      push("mj", "Connect fail: " + e.message);
    }
  };

  const send = async (text) => {
    const t = (text || draft).trim();
    if (!t || busy) return;
    setDraft("");
    push("you", t);
    setBusy(true);
    try {
      const reply = await sendChat({ baseUrl: baseUrl.trim(), apiKey: apiKey.trim(), text: t });
      push("mj", reply);
      setStatus("online");
    } catch (e) {
      push("mj", "Error: " + e.message);
      setStatus("error");
    }
    setBusy(false);
  };

  return (
    <SafeAreaView style={st.root}>
      <StatusBar barStyle="light-content" />
      <View style={st.top}>
        <Text style={st.logo}>MJ</Text>
        <Text style={st.sub}>mobile control</Text>
        <View style={[st.dot, status === "online" ? st.ok : status === "error" ? st.bad : st.off]} />
      </View>
      <View style={st.tabs}>
        <TouchableOpacity onPress={() => setTab("chat")} style={[st.tab, tab === "chat" && st.tabOn]}>
          <Text style={st.tabTxt}>Chat</Text>
        </TouchableOpacity>
        <TouchableOpacity onPress={() => setTab("settings")} style={[st.tab, tab === "settings" && st.tabOn]}>
          <Text style={st.tabTxt}>Settings</Text>
        </TouchableOpacity>
      </View>
      {tab === "settings" ? (
        <View style={st.box}>
          <Text style={st.label}>API URL</Text>
          <TextInput style={st.input} value={baseUrl} onChangeText={setBaseUrl} autoCapitalize="none" />
          <Text style={st.label}>API key</Text>
          <TextInput style={st.input} value={apiKey} onChangeText={setApiKey} autoCapitalize="none" secureTextEntry />
          <TouchableOpacity style={st.btn} onPress={saveSettings}>
            <Text style={st.btnTxt}>Save and ping</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <KeyboardAvoidingView style={{ flex: 1 }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
          <FlatList
            ref={list}
            data={messages}
            keyExtractor={(i) => i.id}
            onContentSizeChange={() => list.current && list.current.scrollToEnd({ animated: true })}
            contentContainerStyle={{ padding: 16 }}
            renderItem={({ item }) => (
              <View style={[st.bubble, item.role === "you" ? st.you : st.mj]}>
                <Text style={st.who}>{item.role === "you" ? "YOU" : "MJ"}</Text>
                <Text style={st.msg}>{item.text}</Text>
              </View>
            )}
          />
          <View style={st.quick}>
            {QUICK.map((q) => (
              <TouchableOpacity key={q.label} style={st.chip} onPress={() => send(q.text)}>
                <Text style={st.chipTxt}>{q.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
          <View style={st.row}>
            <TextInput style={st.compose} placeholder="Hey MJ..." placeholderTextColor="#6b7c99" value={draft} onChangeText={setDraft} onSubmitEditing={() => send()} />
            <TouchableOpacity style={st.send} onPress={() => send()} disabled={busy}>
              <Text style={st.btnTxt}>{busy ? "..." : "Send"}</Text>
            </TouchableOpacity>
          </View>
        </KeyboardAvoidingView>
      )}
    </SafeAreaView>
  );
}

const st = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#05070d" },
  top: { paddingHorizontal: 20, paddingTop: 8, flexDirection: "row", alignItems: "baseline" },
  logo: { color: "#7ee0ff", fontSize: 28, fontWeight: "800", letterSpacing: 3, marginRight: 10 },
  sub: { color: "#6b7c99", flex: 1 },
  dot: { width: 10, height: 10, borderRadius: 5 },
  ok: { backgroundColor: "#3dff9a" },
  bad: { backgroundColor: "#ff5d6c" },
  off: { backgroundColor: "#445066" },
  tabs: { flexDirection: "row", margin: 16, backgroundColor: "#101624", borderRadius: 12 },
  tab: { flex: 1, padding: 12, alignItems: "center" },
  tabOn: { backgroundColor: "#1b2a44", borderRadius: 12 },
  tabTxt: { color: "#d7e6ff", fontWeight: "600" },
  box: { padding: 16 },
  label: { color: "#8aa0c4", marginTop: 8, marginBottom: 6 },
  input: { backgroundColor: "#101624", color: "#fff", borderRadius: 10, padding: 12 },
  btn: { backgroundColor: "#1a6dff", padding: 14, borderRadius: 12, alignItems: "center", marginTop: 12 },
  btnTxt: { color: "#fff", fontWeight: "700" },
  bubble: { maxWidth: "88%", padding: 12, borderRadius: 14, marginBottom: 10 },
  you: { alignSelf: "flex-end", backgroundColor: "#1a6dff" },
  mj: { alignSelf: "flex-start", backgroundColor: "#141c2e" },
  who: { color: "#9fb4d6", fontSize: 10, marginBottom: 4 },
  msg: { color: "#f2f6ff", fontSize: 16, lineHeight: 22 },
  quick: { flexDirection: "row", flexWrap: "wrap", paddingHorizontal: 12 },
  chip: { backgroundColor: "#141c2e", paddingHorizontal: 12, paddingVertical: 8, borderRadius: 20, marginRight: 8, marginBottom: 8 },
  chipTxt: { color: "#7ee0ff" },
  row: { flexDirection: "row", padding: 12, alignItems: "center" },
  compose: { flex: 1, backgroundColor: "#101624", color: "#fff", borderRadius: 12, paddingHorizontal: 14, height: 48, marginRight: 8 },
  send: { backgroundColor: "#1a6dff", height: 48, paddingHorizontal: 16, borderRadius: 12, justifyContent: "center" },
});
