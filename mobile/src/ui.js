import React from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

export const colors = {
  primary: "#2563EB",
  primaryDark: "#1E40AF",
  bg: "#F3F4F6",
  card: "#FFFFFF",
  text: "#111827",
  muted: "#6B7280",
  border: "#D1D5DB",
  danger: "#DC2626",
  success: "#059669",
  chip: "#E5E7EB",
  chipOn: "#2563EB",
};

export function PrimaryButton({ title, onPress, disabled, loading, color }) {
  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.btn,
        { backgroundColor: color || colors.primary, opacity: disabled ? 0.5 : pressed ? 0.85 : 1 },
      ]}
    >
      {loading ? (
        <ActivityIndicator color="#fff" />
      ) : (
        <Text style={styles.btnText}>{title}</Text>
      )}
    </Pressable>
  );
}

export function Section({ title, children }) {
  return (
    <View style={styles.section}>
      {title ? <Text style={styles.sectionTitle}>{title}</Text> : null}
      {children}
    </View>
  );
}

export function Field({ label, value, onChangeText, onBlur, hint, error, keyboardType, multiline }) {
  return (
    <View style={{ marginBottom: 12 }}>
      {label ? <Text style={styles.label}>{label}</Text> : null}
      <TextInput
        style={[styles.input, multiline && { height: 80, textAlignVertical: "top" }, error && { borderColor: colors.danger }]}
        value={value}
        onChangeText={onChangeText}
        onBlur={onBlur}
        keyboardType={keyboardType}
        multiline={multiline}
        placeholderTextColor={colors.muted}
      />
      {hint ? <Text style={styles.hint}>{hint}</Text> : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}
    </View>
  );
}

export function Chip({ label, active, onPress }) {
  return (
    <Pressable
      onPress={onPress}
      style={[styles.chipBase, { backgroundColor: active ? colors.chipOn : colors.chip }]}
    >
      <Text style={{ color: active ? "#fff" : colors.text, fontWeight: "600" }}>{label}</Text>
    </Pressable>
  );
}

/** Single-choice chip group. */
export function ChipGroup({ options, value, onChange }) {
  return (
    <View style={styles.chipWrap}>
      {options.map((o) => (
        <Chip key={o.value} label={o.label} active={value === o.value} onPress={() => onChange(o.value)} />
      ))}
    </View>
  );
}

/** Multi-choice chip group. */
export function MultiChipGroup({ options, values, onChange }) {
  const toggle = (v) =>
    onChange(values.includes(v) ? values.filter((x) => x !== v) : [...values, v]);
  return (
    <View style={styles.chipWrap}>
      {options.map((o) => (
        <Chip key={o.value} label={o.label} active={values.includes(o.value)} onPress={() => toggle(o.value)} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  btn: { paddingVertical: 14, borderRadius: 12, alignItems: "center", marginVertical: 6 },
  btnText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  section: { backgroundColor: colors.card, borderRadius: 14, padding: 16, marginBottom: 14 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: colors.text, marginBottom: 12 },
  label: { fontSize: 13, color: colors.muted, marginBottom: 4 },
  input: {
    borderWidth: 1, borderColor: colors.border, borderRadius: 10,
    paddingHorizontal: 12, paddingVertical: 10, fontSize: 15, color: colors.text,
    backgroundColor: "#fff",
  },
  hint: { fontSize: 12, color: colors.muted, marginTop: 3 },
  error: { fontSize: 12, color: colors.danger, marginTop: 3 },
  chipWrap: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chipBase: { paddingHorizontal: 14, paddingVertical: 9, borderRadius: 20 },
});
