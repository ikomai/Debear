import React, { useCallback, useState } from "react";
import { ActivityIndicator, FlatList, Pressable, RefreshControl, Text, View, StyleSheet } from "react-native";
import { useFocusEffect } from "@react-navigation/native";
import { listApplications } from "../api";
import { colors } from "../ui";

export default function MyApplicationsScreen({ navigation }) {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setError(null);
      setItems(await listApplications());
    } catch (e) {
      setError("Couldn't load applications. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(useCallback(() => { setLoading(true); load(); }, [load]));

  if (loading) return <ActivityIndicator style={{ marginTop: 40 }} color={colors.primary} />;

  if (error) return <Text style={styles.error}>{error}</Text>;

  if (!items.length)
    return <Text style={styles.empty}>You don't have any applications yet.</Text>;

  return (
    <FlatList
      contentContainerStyle={{ padding: 16 }}
      data={items}
      keyExtractor={(i) => String(i.id)}
      refreshControl={<RefreshControl refreshing={false} onRefresh={load} />}
      renderItem={({ item }) => (
        <Pressable style={styles.card} onPress={() => navigation.navigate("ApplicationDetail", { id: item.id })}>
          <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
            <Text style={styles.number}>#{item.number}</Text>
            <Text style={styles.status}>{item.status_label}</Text>
          </View>
          <Text style={styles.meta}>{item.property_type_label}</Text>
          <Text style={styles.meta}>
            Sum: {item.insured_sum ? item.insured_sum.toLocaleString() : "—"} · {item.term_months || "—"} mo
          </Text>
        </Pressable>
      )}
    />
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.card, borderRadius: 12, padding: 16, marginBottom: 12 },
  number: { fontSize: 17, fontWeight: "700", color: colors.text },
  status: { fontSize: 14, fontWeight: "700", color: colors.primary },
  meta: { fontSize: 14, color: colors.muted, marginTop: 4 },
  empty: { textAlign: "center", marginTop: 40, color: colors.muted, fontSize: 15 },
  error: { textAlign: "center", marginTop: 40, color: colors.danger, fontSize: 15, paddingHorizontal: 20 },
});
