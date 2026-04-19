import React, {useCallback, useEffect, useRef, useState} from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator,
  Share, FlatList, Dimensions, ViewToken,
} from 'react-native';
import {colors} from '../constants/colors';
import Icon from 'react-native-vector-icons/Ionicons';
import {fetchDailyQuote, fetchRecommend} from '../api/client';
import {useFavorites} from '../hooks/useFavorites';
import {getPreference} from '../storage/preferences';
import {logInteraction} from '../storage/interactions';
import {useInteractionSync} from '../hooks/useInteractionSync';
import {useProfile} from '../hooks/useProfile';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';

const {height: SCREEN_HEIGHT} = Dimensions.get('window');
const DWELL_THRESHOLD_MS = 3000;
const VIEWABILITY_CONFIG = {itemVisiblePercentThreshold: 70};

export function HomeScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const {toggle, isFav} = useFavorites();
  const prefRef = useRef<Record<string, string> | undefined>();
  const seenIdsRef = useRef<Set<string>>(new Set());
  const dwellTimers = useRef<Map<string, number>>(new Map());
  const profile = useProfile();

  useInteractionSync();

  useEffect(() => {
    getPreference().then(pref => {
      const params: Record<string, string> = {};
      if (pref) {
        params.situations = pref.situation_groups.join(',');
        params.keywords = pref.keyword_groups.join(',');
      }
      // 프로필 가중치가 있으면 추천 파라미터에 포함
      if (profile && profile.total_interactions >= 5) {
        params.kw_weights = JSON.stringify(profile.keyword_weights);
        params.sit_weights = JSON.stringify(profile.situation_weights);
        params.profile_strength = profile.profile_strength;
      }
      prefRef.current = Object.keys(params).length > 0 ? params : undefined;
      return fetchDailyQuote(prefRef.current);
    })
      .then(q => {
        setQuotes([q]);
        seenIdsRef.current.add(q.id);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [profile]);

  const loadMore = useCallback(async () => {
    if (loadingMore) return;
    setLoadingMore(true);
    try {
      const exclude = Array.from(seenIdsRef.current).join(',');
      const newQuotes = await fetchRecommend({
        ...(prefRef.current || {}),
        exclude,
        limit: '3',
      });
      const fresh = newQuotes.filter(q => !seenIdsRef.current.has(q.id));
      fresh.forEach(q => seenIdsRef.current.add(q.id));
      if (fresh.length > 0) {
        setQuotes(prev => [...prev, ...fresh]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoadingMore(false);
    }
  }, [loadingMore]);

  const handleShare = async (q: Quote) => {
    const author = q.author?.name || '알 수 없음';
    await Share.share({message: `"${q.text}"\n\n— ${author}`});
    logInteraction({quote_id: q.id, type: 'share'});
  };

  const onViewableItemsChanged = useRef(({changed}: {changed: ViewToken[]}) => {
    for (const token of changed) {
      const quoteId = (token.item as Quote)?.id;
      if (!quoteId) continue;
      if (token.isViewable) {
        dwellTimers.current.set(quoteId, Date.now());
      } else {
        const start = dwellTimers.current.get(quoteId);
        if (start) {
          const elapsed = Date.now() - start;
          if (elapsed >= DWELL_THRESHOLD_MS) {
            logInteraction({
              quote_id: quoteId,
              type: 'dwell',
              metadata: {dwell_seconds: Math.round(elapsed / 1000)},
            });
          }
          dwellTimers.current.delete(quoteId);
        }
      }
    }
  }).current;

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (quotes.length === 0) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>명언을 불러올 수 없습니다.</Text>
      </View>
    );
  }

  const renderQuote = ({item, index}: {item: Quote; index: number}) => {
    const fav = isFav(item.id);
    return (
      <View style={[styles.page, {height: SCREEN_HEIGHT - 100}]}>
        <Text style={styles.label}>
          {index === 0 ? '오늘의 명언' : '추천 명언'}
        </Text>

        <TouchableOpacity
          style={styles.quoteArea}
          activeOpacity={0.8}
          onPress={() => navigation.navigate('QuoteDetail', {quoteId: item.id})}>
          <Text style={styles.quoteText}>"{item.text}"</Text>
          {item.text_original && item.text_original !== item.text && (
            <Text style={styles.originalText}>{item.text_original}</Text>
          )}
          <Text style={styles.author}>— {item.author?.name}</Text>
          {item.author?.profession && (
            <Text style={styles.profession}>{item.author.profession}</Text>
          )}
        </TouchableOpacity>

        <View style={styles.actions}>
          <TouchableOpacity style={styles.actionBtn} onPress={() => toggle(item.id)}>
            <Icon name={fav ? 'thumbs-up' : 'thumbs-up-outline'} size={26} color={fav ? colors.success : colors.textSecondary} />
            <Text style={styles.actionLabel}>좋아요</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionBtn} onPress={() => {
            logInteraction({quote_id: item.id, type: 'unlike'});
          }}>
            <Icon name="thumbs-down-outline" size={26} color={colors.textSecondary} />
            <Text style={styles.actionLabel}>별로예요</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.actionBtn} onPress={() => handleShare(item)}>
            <Icon name="share-outline" size={26} color={colors.textSecondary} />
            <Text style={styles.actionLabel}>공유</Text>
          </TouchableOpacity>
        </View>

        {item.keywords && item.keywords.length > 0 && (
          <View style={styles.tags}>
            {item.keywords.map(k => (
              <View key={k} style={styles.tag}>
                <Text style={styles.tagText}>#{k}</Text>
              </View>
            ))}
          </View>
        )}

        {index === 0 && (
          <Text style={styles.swipeHint}>↑ 위로 스와이프하면 다음 명언</Text>
        )}
      </View>
    );
  };

  return (
    <FlatList
      data={quotes}
      keyExtractor={item => item.id}
      renderItem={renderQuote}
      pagingEnabled
      snapToAlignment="start"
      decelerationRate="fast"
      snapToInterval={SCREEN_HEIGHT - 100}
      showsVerticalScrollIndicator={false}
      style={styles.container}
      onEndReached={loadMore}
      onEndReachedThreshold={0.5}
      onViewableItemsChanged={onViewableItemsChanged}
      viewabilityConfig={VIEWABILITY_CONFIG}
      ListFooterComponent={
        loadingMore ? (
          <View style={styles.footer}>
            <ActivityIndicator size="small" color={colors.primary} />
          </View>
        ) : null
      }
    />
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  page: {justifyContent: 'center', padding: 24},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  errorText: {color: colors.textSecondary, fontSize: 16},
  label: {color: colors.textMuted, fontSize: 14, textAlign: 'center', marginBottom: 24, letterSpacing: 2, textTransform: 'uppercase'},
  quoteArea: {alignItems: 'center'},
  quoteText: {color: colors.text, fontSize: 22, lineHeight: 36, textAlign: 'center', fontWeight: '300'},
  originalText: {color: colors.textMuted, fontSize: 14, textAlign: 'center', marginTop: 12, fontStyle: 'italic'},
  author: {color: colors.primary, fontSize: 16, marginTop: 24, fontWeight: '500'},
  profession: {color: colors.textMuted, fontSize: 13, marginTop: 4},
  actions: {flexDirection: 'row', justifyContent: 'center', gap: 40, marginTop: 40},
  actionBtn: {alignItems: 'center'},
  actionIcon: {fontSize: 28, color: colors.textSecondary},
  actionLabel: {color: colors.textMuted, fontSize: 12, marginTop: 4},
  tags: {flexDirection: 'row', justifyContent: 'center', flexWrap: 'wrap', gap: 8, marginTop: 32},
  tag: {backgroundColor: colors.surfaceLight, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 5},
  tagText: {color: colors.textSecondary, fontSize: 13},
  swipeHint: {color: colors.textMuted, fontSize: 12, textAlign: 'center', marginTop: 32, opacity: 0.6},
  footer: {height: 60, justifyContent: 'center', alignItems: 'center'},
});
