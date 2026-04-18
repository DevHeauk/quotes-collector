import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = '@user_preference';

export interface UserPreference {
  situation_groups: string[];
  keyword_groups: string[];
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
}

export async function getPreference(): Promise<UserPreference | null> {
  const raw = await AsyncStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function savePreference(
  situations: string[],
  keywords: string[],
): Promise<void> {
  const existing = await getPreference();
  const now = new Date().toISOString();
  const pref: UserPreference = {
    situation_groups: situations,
    keyword_groups: keywords,
    onboarding_completed: true,
    created_at: existing?.created_at || now,
    updated_at: now,
  };
  await AsyncStorage.setItem(KEY, JSON.stringify(pref));
}

export async function isOnboardingCompleted(): Promise<boolean> {
  const pref = await getPreference();
  return pref?.onboarding_completed ?? false;
}

export async function clearPreference(): Promise<void> {
  await AsyncStorage.removeItem(KEY);
}
