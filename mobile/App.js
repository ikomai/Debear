import React from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { StatusBar } from "expo-status-bar";

import { colors } from "./src/ui";
import HomeScreen from "./src/screens/Home";
import NewApplicationScreen from "./src/screens/NewApplication";
import MyApplicationsScreen from "./src/screens/MyApplications";
import ApplicationDetailScreen from "./src/screens/ApplicationDetail";
import HelpScreen from "./src/screens/Help";
import ContactScreen from "./src/screens/Contact";

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <StatusBar style="light" />
      <Stack.Navigator
        screenOptions={{
          headerStyle: { backgroundColor: colors.primary },
          headerTintColor: "#fff",
          headerTitleStyle: { fontWeight: "700" },
          contentStyle: { backgroundColor: colors.bg },
        }}
      >
        <Stack.Screen name="Home" component={HomeScreen} options={{ title: "Debear" }} />
        <Stack.Screen name="NewApplication" component={NewApplicationScreen} options={{ title: "Apply for insurance" }} />
        <Stack.Screen name="MyApplications" component={MyApplicationsScreen} options={{ title: "My applications" }} />
        <Stack.Screen name="ApplicationDetail" component={ApplicationDetailScreen} options={{ title: "Application" }} />
        <Stack.Screen name="Help" component={HelpScreen} options={{ title: "Help" }} />
        <Stack.Screen name="Contact" component={ContactScreen} options={{ title: "Contact a manager" }} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
