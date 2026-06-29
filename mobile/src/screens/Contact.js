import React from "react";
import { ScrollView, Text, StyleSheet, Linking } from "react-native";
import { colors, PrimaryButton } from "../ui";

export default function ContactScreen() {
  return (
    <ScrollView contentContainerStyle={styles.c}>
      <Text style={styles.h}>☎ Contact a manager</Text>
      <Text style={styles.p}>Write to @Ur_Oper or call +0 000 000-00-00.</Text>
      <Text style={styles.p}>Working hours: Mon–Fri, 9:00–18:00.</Text>
      <PrimaryButton title="Open @Ur_Oper in Telegram" onPress={() => Linking.openURL("https://t.me/Ur_Oper")} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  c: { padding: 20 },
  h: { fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 12 },
  p: { fontSize: 15, color: colors.text, marginBottom: 10, lineHeight: 21 },
});
