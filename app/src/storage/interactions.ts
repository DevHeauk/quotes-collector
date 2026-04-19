import AsyncStorage from '@react-native-async-storage/async-storage';
import {API_BASE_URL} from '../constants/config';
import {getDeviceId} from './deviceId';

const KEY = '@interactions';

export interface Interaction {
  quote_id: string;
  type: 'like' | 'unlike' | 'share' | 'view_detail' | 'dwell';
  timestamp: string;
  metadata?: {dwell_seconds?: number};
}

async function getQueue(): Promise<Interaction[]> {
  const raw = await AsyncStorage.getItem(KEY);
  return raw ? JSON.parse(raw) : [];
}

export async function logInteraction(interaction: Omit<Interaction, 'timestamp'>): Promise<void> {
  const queue = await getQueue();
  queue.push({...interaction, timestamp: new Date().toISOString()});
  await AsyncStorage.setItem(KEY, JSON.stringify(queue));
}

export async function syncInteractions(): Promise<void> {
  const queue = await getQueue();
  if (queue.length === 0) return;

  const deviceId = await getDeviceId();
  try {
    const res = await fetch(`${API_BASE_URL}/app/api/v1/interactions`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({device_id: deviceId, interactions: queue}),
    });
    if (res.ok) {
      await AsyncStorage.setItem(KEY, JSON.stringify([]));
    }
  } catch {
    // 네트워크 실패 시 다음 동기화에서 재시도
  }
}
