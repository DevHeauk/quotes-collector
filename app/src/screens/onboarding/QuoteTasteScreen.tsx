import React, {useEffect, useState} from 'react';
import {View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, ScrollView, Alert} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {colors} from '../../constants/colors';
import Icon from 'react-native-vector-icons/Ionicons';
import {fetchRecommend} from '../../api/client';
import {savePreference} from '../../storage/preferences';
import {addFavorite} from '../../storage/favorites';
import type {Quote} from '../../types';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {OnboardingStackParamList} from '../../types/navigation';

type Props = NativeStackScreenProps<OnboardingStackParamList, 'QuoteTaste'>;

export function QuoteTasteScreen({navigation, route}: Props) {
  const {situations, keywords} = route.params;
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [liked, setLiked] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);

  const loadQuotes = () => {
    setLoading(true);
    setError(false);
    fetchRecommend({
      situations: situations.join(','),
      keywords: keywords.join(','),
      limit: '3',
    })
      .then(setQuotes)
      .catch(() => setError(true))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadQuotes();
  }, [situations, keywords]);

  const toggleLike = (id: string) => {
    setLiked(prev => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleComplete = async () => {
    setSaving(true);
    try {
      await savePreference(situations, keywords);
      for (const id of liked) {
        await addFavorite(id);
      }
      navigation.reset({index: 0, routes: [{name: 'Main'}]});
    } catch (e) {
      Alert.alert('오류', '설정 저장에 실패했습니다. 다시 시도해 주세요.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>당신을 위한 명언을 고르는 중...</Text>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.center}>
        <Text style={styles.errorText}>명언을 불러오지 못했습니다.</Text>
        <TouchableOpacity style={styles.retryBtn} onPress={loadQuotes}>
          <Text style={styles.retryText}>다시 시도</Text>
        </TouchableOpacity>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.step}>3 / 3</Text>
        <Text style={styles.title}>마음에 드는 명언을{'\n'}골라보세요</Text>
        <Text style={styles.subtitle}>취향을 파악하는 데 도움이 돼요</Text>
      </View>

      <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
        {quotes.map(q => {
          const isLiked = liked.has(q.id);
          return (
            <TouchableOpacity
              key={q.id}
              style={[styles.card, isLiked && styles.cardLiked]}
              onPress={() => toggleLike(q.id)}
              activeOpacity={0.8}>
              <Text style={styles.quoteText}>"{q.text}"</Text>
              <View style={styles.cardBottom}>
                <Text style={styles.author}>— {q.author?.name || q.author_name}</Text>
                <Icon
                  name={isLiked ? 'heart' : 'heart-outline'}
                  size={26}
                  color={isLiked ? colors.heart : colors.heartInactive}
                />
              </View>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      <TouchableOpacity style={styles.startBtn} onPress={handleComplete} disabled={saving}>
        <Text style={styles.startText}>{saving ? '설정 중...' : '시작하기'}</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background, padding: 24},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  loadingText: {color: colors.textMuted, fontSize: 14, marginTop: 16},
  errorText: {color: colors.textMuted, fontSize: 16, marginBottom: 16},
  retryBtn: {backgroundColor: colors.primary, borderRadius: 10, paddingHorizontal: 24, paddingVertical: 12},
  retryText: {color: colors.background, fontSize: 14, fontWeight: '600'},
  header: {marginTop: 20, marginBottom: 24},
  step: {color: colors.primary, fontSize: 14, fontWeight: '600', marginBottom: 8},
  title: {color: colors.text, fontSize: 24, fontWeight: '700', marginBottom: 8},
  subtitle: {color: colors.textMuted, fontSize: 14},
  scroll: {flex: 1, marginBottom: 80},
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  cardLiked: {borderColor: colors.heart, backgroundColor: '#2a1525'},
  quoteText: {color: colors.text, fontSize: 16, lineHeight: 28, fontWeight: '300'},
  cardBottom: {flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginTop: 16},
  author: {color: colors.textSecondary, fontSize: 14},
  heart: {fontSize: 28, color: colors.heartInactive},
  heartActive: {color: colors.heart},
  startBtn: {
    position: 'absolute',
    bottom: 40,
    left: 24,
    right: 24,
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  startText: {color: colors.background, fontSize: 16, fontWeight: '700'},
});
