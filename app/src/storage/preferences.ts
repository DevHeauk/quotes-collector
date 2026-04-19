import AsyncStorage from '@react-native-async-storage/async-storage';

const KEY = '@user_preference';

export interface UserPreference {
  needs: string[];
  onboarding_completed: boolean;
  created_at: string;
  updated_at: string;
  /** @deprecated 기존 온보딩 데이터. 신규 코드에서 사용 금지. */
  situation_groups?: string[];
  /** @deprecated 기존 온보딩 데이터. 신규 코드에서 사용 금지. */
  keyword_groups?: string[];
}

export async function getPreference(): Promise<UserPreference | null> {
  const raw = await AsyncStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : null;
}

export async function savePreference(needs: string[]): Promise<void> {
  const existing = await getPreference();
  const now = new Date().toISOString();
  const pref: UserPreference = {
    needs,
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
