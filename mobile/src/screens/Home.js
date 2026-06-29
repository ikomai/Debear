import React from "react";
import { ScrollView, Text, View, StyleSheet } from "react-native";
import { PrimaryButton, colors } from "../ui";

export default function HomeScreen({ navigation }) {
  return (
    <ScrollView contentContainerStyle={styles.container}>
      <View style={styles.hero}>
        <Text style={styles.logo}>🐻 Debear</Text>
        <Text style={styles.subtitle}>Real-estate insurance in a few taps</Text>
      </View>

      <PrimaryButton title="🏠 Apply for insurance" onPress={() => navigation.navigate("NewApplication")} />
      <PrimaryButton title="📋 My applications" onPress={() => navigation.navigate("MyApplications")} color={colors.primaryDark} />
      <PrimaryButton title="❓ Help" onPress={() => navigation.navigate("Help")} color="#475569" />
      <PrimaryButton title="☎ Contact a manager" onPress={() => navigation.navigate("Contact")} color="#475569" />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { padding: 20 },
  hero: { alignItems: "center", marginVertical: 28 },
  logo: { fontSize: 36, fontWeight: "800", color: colors.primary },
  subtitle: { fontSize: 15, color: colors.muted, marginTop: 6 },
});
