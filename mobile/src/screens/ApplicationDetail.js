import React, { useEffect, useState } from "react";
import { ActivityIndicator, Linking, ScrollView, Text, View, StyleSheet } from "react-native";
import { getApplication, pdfUrl } from "../api";
import { PrimaryButton, colors } from "../ui";

function Row({ label, value }) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <Text style={styles.rowValue}>{value || "—"}</Text>
    </View>
  );
}

export default function ApplicationDetailScreen({ route }) {
  const { id } = route.params;
  const [data, setData] = useState(null);

  useEffect(() => {
    getApplication(id).then(setData).catch(() => setData(false));
  }, [id]);

  if (data === null) return <ActivityIndicator style={{ marginTop: 40 }} color={colors.primary} />;
  if (data === false) return <Text style={styles.err}>Couldn't load this application.</Text>;

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      <View style={styles.head}>
        <Text style={styles.number}>#{data.number}</Text>
        <Text style={styles.status}>{data.status_label}</Text>
      </View>
      <View style={styles.card}>
        <Row label="Property type" value={data.property_type_label} />
        <Row label="Address" value={data.address} />
        <Row label="Owner" value={data.owner} />
        <Row label="Insured sum" value={data.insured_sum ? data.insured_sum.toLocaleString() : "—"} />
        <Row label="Term" value={data.term_months ? `${data.term_months} months` : "—"} />
        <Row label="Coverage" value={data.coverage} />
        <Row label="Risks" value={data.risks} />
      </View>
      <PrimaryButton title="📄 Open application PDF" onPress={() => Linking.openURL(pdfUrl(id))} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  head: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  number: { fontSize: 22, fontWeight: "800", color: colors.text },
  status: { fontSize: 15, fontWeight: "700", color: colors.primary },
  card: { backgroundColor: colors.card, borderRadius: 12, padding: 16, marginBottom: 16 },
  row: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#F1F1F1" },
  rowLabel: { color: colors.muted, fontSize: 14, flex: 1 },
  rowValue: { color: colors.text, fontSize: 14, fontWeight: "600", flex: 1.4, textAlign: "right" },
  err: { textAlign: "center", marginTop: 40, color: colors.danger },
});
