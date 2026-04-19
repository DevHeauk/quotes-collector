import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = '@admin_token';

export async function getAdminToken(): Promise<string | null> {
  return AsyncStorage.getItem(KEY);
}

export async function setAdminToken(token: string): Promise<void> {
  await AsyncStorage.setItem(KEY, token);
}

export async function clearAdminToken(): Promise<void> {
  await AsyncStorage.removeItem(KEY);
}
