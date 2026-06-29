import React, { useEffect, useState } from "react";
import { ActivityIndicator, Alert, Pressable, ScrollView, Text, View, StyleSheet } from "react-native";
import { getMeta, validateField, createApplication } from "../api";
import {
  Section, Field, ChipGroup, MultiChipGroup, Chip, PrimaryButton, colors,
} from "../ui";

const ADDITIONAL = [
  ["Security alarm", "Is there a security alarm?"],
  ["Video surveillance", "Is there video surveillance (CCTV)?"],
  ["Previous claims", "Any previous insurance claims?"],
  ["Tenants present", "Are there tenants?"],
  ["Currently vacant", "Is the property vacant?"],
  ["Used for business", "Used for business?"],
];

function YesNo({ value, onChange }) {
  return (
    <View style={{ flexDirection: "row", gap: 8 }}>
      <Chip label="Yes" active={value === "Yes"} onPress={() => onChange("Yes")} />
      <Chip label="No" active={value === "No"} onPress={() => onChange("No")} />
    </View>
  );
}

export default function NewApplicationScreen({ navigation }) {
  const [meta, setMeta] = useState(null);
  const [metaError, setMetaError] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [vstate, setVstate] = useState({}); // address validation feedback
  const [form, setForm] = useState({
    has_mortgage: "no",
    coverage: [],
    risks: [],
    extra: Object.fromEntries(ADDITIONAL.map(([k]) => [k, "No"])),
    term: "12",
    consent: false,
  });

  useEffect(() => {
    getMeta().then(setMeta).catch(() => setMetaError(true));
  }, []);

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const setExtra = (k, v) => setForm((f) => ({ ...f, extra: { ...f.extra, [k]: v } }));

  async function checkAddress(kind, field) {
    const value = (form[field] || "").trim();
    if (!value) return;
    const ctx = kind === "city" ? { country: form.country } : kind === "street" ? { country: form.country, city: form.city } : {};
    try {
      const r = await validateField(kind, value, ctx);
      if (r.ok) {
        if (r.value && r.value !== value) set(field, r.value);
        setVstate((s) => ({ ...s, [field]: null }));
      } else {
        setVstate((s) => ({ ...s, [field]: { message: r.message, suggestions: r.suggestions || [] } }));
      }
    } catch {
      setVstate((s) => ({ ...s, [field]: null })); // soft-accept if backend unreachable
    }
  }

  function pickSuggestion(field, value) {
    set(field, value);
    setVstate((s) => ({ ...s, [field]: null }));
  }

  function AddressFeedback({ field }) {
    const v = vstate[field];
    if (!v) return null;
    return (
      <View style={{ marginTop: -6, marginBottom: 12 }}>
        <Text style={{ color: colors.danger, fontSize: 12, marginBottom: 6 }}>{v.message}</Text>
        <View style={{ flexDirection: "row", flexWrap: "wrap", gap: 8 }}>
          {v.suggestions.map((s) => (
            <Chip key={s} label={s} active={false} onPress={() => pickSuggestion(field, s)} />
          ))}
        </View>
      </View>
    );
  }

  async function onSubmit() {
    if (!form.property_type || !form.owner_name || !form.phone || !form.email) {
      Alert.alert("Missing data", "Please fill in property type, owner name, phone and email.");
      return;
    }
    if (!form.consent) {
      Alert.alert("Consent required", "Please agree to the processing of personal data.");
      return;
    }
    setSubmitting(true);
    try {
      const payload = { ...form };
      delete payload.consent;
      payload.insured_sum = form.insured_sum ? Number(String(form.insured_sum).replace(/[^\d.]/g, "")) : null;
      const app = await createApplication(payload);
      Alert.alert("Submitted", `Your application #${app.number} has been created.`);
      navigation.replace("ApplicationDetail", { id: app.id });
    } catch (e) {
      Alert.alert("Error", "Couldn't submit. Is the backend running and reachable?");
    } finally {
      setSubmitting(false);
    }
  }

  if (metaError)
    return <Text style={styles.err}>Couldn't reach the backend. Start it with{"\n"}uvicorn api.main:app --host 0.0.0.0 --port 8000</Text>;
  if (!meta) return <ActivityIndicator style={{ marginTop: 40 }} color={colors.primary} />;

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }} keyboardShouldPersistTaps="handled">
      <Section title="Property">
        <Text style={styles.lbl}>Type</Text>
        <ChipGroup options={meta.property_types} value={form.property_type} onChange={(v) => set("property_type", v)} />
        <Text style={[styles.lbl, { marginTop: 12 }]}>Purpose</Text>
        <ChipGroup options={meta.purposes} value={form.purpose} onChange={(v) => set("purpose", v)} />
      </Section>

      <Section title="Address (checked against real locations)">
        <Field label="Country" value={form.country} onChangeText={(v) => set("country", v)} onBlur={() => checkAddress("country", "country")} />
        <AddressFeedback field="country" />
        <Field label="Region / state" value={form.region} onChangeText={(v) => set("region", v)} />
        <Field label="City" value={form.city} onChangeText={(v) => set("city", v)} onBlur={() => checkAddress("city", "city")} />
        <AddressFeedback field="city" />
        <Field label="Street" value={form.street} onChangeText={(v) => set("street", v)} onBlur={() => checkAddress("street", "street")} />
        <AddressFeedback field="street" />
        <Field label="House" value={form.house} onChangeText={(v) => set("house", v)} />
        <Field label="Building / block" value={form.building} onChangeText={(v) => set("building", v)} />
        <Field label="Apartment" value={form.apartment} onChangeText={(v) => set("apartment", v)} />
        <Field label="Postal code" value={form.postal_code} onChangeText={(v) => set("postal_code", v)} keyboardType="numbers-and-punctuation" />
      </Section>

      <Section title="Property details">
        <Field label="Year built" value={form.year_built} onChangeText={(v) => set("year_built", v)} keyboardType="number-pad" />
        <Field label="Total floors" value={form.floors_total} onChangeText={(v) => set("floors_total", v)} keyboardType="number-pad" />
        <Field label="Floor" value={form.floor} onChangeText={(v) => set("floor", v)} keyboardType="number-pad" />
        <Field label="Total area, m²" value={form.total_area} onChangeText={(v) => set("total_area", v)} keyboardType="decimal-pad" />
        <Field label="Living area, m²" value={form.living_area} onChangeText={(v) => set("living_area", v)} keyboardType="decimal-pad" />
        <Field label="Wall material" value={form.wall_material} onChangeText={(v) => set("wall_material", v)} />
        <Field label="Ceiling material" value={form.ceiling_material} onChangeText={(v) => set("ceiling_material", v)} />
        <Text style={styles.lbl}>Renovation</Text>
        <ChipGroup options={meta.renovation} value={form.renovation} onChange={(v) => set("renovation", v)} />
        <View style={{ height: 12 }} />
        <Field label="Estimated value" value={form.value} onChangeText={(v) => set("value", v)} keyboardType="decimal-pad" />
        <Field label="Cadastral number (optional)" value={form.cadastral_number} onChangeText={(v) => set("cadastral_number", v)} />
      </Section>

      <Section title="Owner">
        <Field label="Full name" value={form.owner_name} onChangeText={(v) => set("owner_name", v)} />
        <Field label="Date of birth (DD.MM.YYYY)" value={form.birth_date} onChangeText={(v) => set("birth_date", v)} />
        <Text style={styles.lbl}>Gender</Text>
        <ChipGroup options={meta.genders} value={form.gender} onChange={(v) => set("gender", v)} />
        <View style={{ height: 12 }} />
        <Field label="Phone" value={form.phone} onChangeText={(v) => set("phone", v)} keyboardType="phone-pad" />
        <Field label="Email" value={form.email} onChangeText={(v) => set("email", v)} keyboardType="email-address" />
        <Field label="Tax ID / INN (optional)" value={form.inn} onChangeText={(v) => set("inn", v)} />
        <Field label="Passport series" value={form.passport_series} onChangeText={(v) => set("passport_series", v)} />
        <Field label="Passport number" value={form.passport_number} onChangeText={(v) => set("passport_number", v)} />
        <Field label="Issued by" value={form.passport_issued_by} onChangeText={(v) => set("passport_issued_by", v)} multiline />
        <Field label="Issue date (DD.MM.YYYY)" value={form.passport_issue_date} onChangeText={(v) => set("passport_issue_date", v)} />
      </Section>

      <Section title="Mortgage">
        <Text style={styles.lbl}>Is the property under a mortgage?</Text>
        <View style={{ flexDirection: "row", gap: 8 }}>
          <Chip label="Yes" active={form.has_mortgage === "yes"} onPress={() => set("has_mortgage", "yes")} />
          <Chip label="No" active={form.has_mortgage === "no"} onPress={() => set("has_mortgage", "no")} />
        </View>
        {form.has_mortgage === "yes" && (
          <View style={{ marginTop: 12 }}>
            <Field label="Bank" value={form.bank} onChangeText={(v) => set("bank", v)} />
            <Field label="Contract number" value={form.contract_number} onChangeText={(v) => set("contract_number", v)} />
            <Field label="Contract date (DD.MM.YYYY)" value={form.contract_date} onChangeText={(v) => set("contract_date", v)} />
            <Field label="Outstanding debt" value={form.debt_balance} onChangeText={(v) => set("debt_balance", v)} keyboardType="decimal-pad" />
          </View>
        )}
      </Section>

      <Section title="What to insure">
        <MultiChipGroup options={meta.coverage} values={form.coverage} onChange={(v) => set("coverage", v)} />
      </Section>

      <Section title="Risks to cover">
        <MultiChipGroup options={meta.risks} values={form.risks} onChange={(v) => set("risks", v)} />
      </Section>

      <Section title="Sum & term">
        <Field label="Insured sum" value={form.insured_sum} onChangeText={(v) => set("insured_sum", v)} keyboardType="decimal-pad" />
        <Text style={styles.lbl}>Term</Text>
        <ChipGroup options={meta.terms} value={form.term} onChange={(v) => set("term", v)} />
      </Section>

      <Section title="Additional questions">
        {ADDITIONAL.map(([key, q]) => (
          <View key={key} style={{ marginBottom: 12 }}>
            <Text style={styles.lbl}>{q}</Text>
            <YesNo value={form.extra[key]} onChange={(v) => setExtra(key, v)} />
          </View>
        ))}
      </Section>

      <Section>
        <Pressable style={styles.consent} onPress={() => set("consent", !form.consent)}>
          <Text style={{ fontSize: 20 }}>{form.consent ? "☑️" : "⬜"}</Text>
          <Text style={styles.consentText}>I agree to the processing of my personal data.</Text>
        </Pressable>
      </Section>

      <PrimaryButton title="✅ Submit application" onPress={onSubmit} loading={submitting} color={colors.success} />
      <View style={{ height: 30 }} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  lbl: { fontSize: 13, color: colors.muted, marginBottom: 6 },
  consent: { flexDirection: "row", alignItems: "center", gap: 10 },
  consentText: { flex: 1, color: colors.text, fontSize: 14 },
  err: { textAlign: "center", marginTop: 40, color: colors.danger, paddingHorizontal: 20, lineHeight: 20 },
});
