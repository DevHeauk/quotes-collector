import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = '@favorites';

export async function getFavorites(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function addFavorite(id: string): Promise<void> {
  const list = await getFavorites();
  if (!list.includes(id)) {
    list.unshift(id);
    await AsyncStorage.setItem(KEY, JSON.stringify(list));
  }
}

export async function removeFavorite(id: string): Promise<void> {
  const list = await getFavorites();
  await AsyncStorage.setItem(KEY, JSON.stringify(list.filter(x => x !== id)));
}
