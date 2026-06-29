import React from "react";
import { ScrollView, Text, StyleSheet } from "react-native";
import { colors } from "../ui";

export default function HelpScreen() {
  return (
    <ScrollView contentContainerStyle={styles.c}>
      <Text style={styles.h}>How it works</Text>
      <Text style={styles.p}>1. Tap “Apply for insurance” and fill in the form.</Text>
      <Text style={styles.p}>2. The address fields are checked against real locations.</Text>
      <Text style={styles.p}>3. Review and submit your application.</Text>
      <Text style={styles.p}>4. A manager will contact you. Track the status in “My applications”.</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  c: { padding: 20 },
  h: { fontSize: 20, fontWeight: "700", color: colors.text, marginBottom: 12 },
  p: { fontSize: 15, color: colors.text, marginBottom: 10, lineHeight: 21 },
});
