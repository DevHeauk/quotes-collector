import React, {useCallback, useEffect, useRef, useState} from 'react';
import {
  View, Text, TouchableOpacity, StyleSheet, ActivityIndicator,
  Share, Dimensions, Animated, PanResponder,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
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

const {width: SCREEN_WIDTH, height: SCREEN_HEIGHT} = Dimensions.get('window');
const SWIPE_THRESHOLD = 120;
const SWIPE_OUT_DURATION = 300;
const CARD_HEIGHT = SCREEN_HEIGHT * 0.55;
const HINT_KEY = '@swipe_hint_shown';

export function HomeScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [quotes, setQuotes] = useState<Quote[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showHint, setShowHint] = useState(false);
  const [lastSwiped, setLastSwiped] = useState<{quote: Quote; index: number} | null>(null);
  const {toggle, isFav} = useFavorites();
  const prefRef = useRef<Record<string, string> | undefined>();
  const seenIdsRef = useRef<Set<string>>(new Set());
  const loadingMoreRef = useRef(false);
  const profile = useProfile();
  const position = useRef(new Animated.ValueXY()).current;
  const hintOpacity = useRef(new Animated.Value(0)).current;
  const swipeCallbackRef = useRef<(dir: 'left' | 'right') => void>();

  useInteractionSync();

  // 힌트 체크
  useEffect(() => {
    AsyncStorage.getItem(HINT_KEY).then(v => {
      if (!v) setShowHint(true);
    });
  }, []);

  // 힌트 애니메이션
  useEffect(() => {
    if (!showHint || loading) return;
    const timer = setTimeout(() => {
      Animated.sequence([
        Animated.timing(hintOpacity, {toValue: 1, duration: 500, useNativeDriver: true}),
        Animated.timing(position, {toValue: {x: -40, y: 0}, duration: 400, useNativeDriver: true}),
        Animated.timing(position, {toValue: {x: 40, y: 0}, duration: 600, useNativeDriver: true}),
        Animated.timing(position, {toValue: {x: 0, y: 0}, duration: 400, useNativeDriver: true}),
        Animated.delay(500),
        Animated.timing(hintOpacity, {toValue: 0, duration: 500, useNativeDriver: true}),
      ]).start();
    }, 1500);
    return () => clearTimeout(timer);
  }, [showHint, loading, hintOpacity, position]);

  // 초기 로딩
  useEffect(() => {
    getPreference().then(async pref => {
      const params: Record<string, string> = {};
      if (pref) {
        params.situations = pref.situation_groups.join(',');
        params.keywords = pref.keyword_groups.join(',');
      }
      if (profile && profile.total_interactions >= 5) {
        params.kw_weights = JSON.stringify(profile.keyword_weights);
        params.sit_weights = JSON.stringify(profile.situation_weights);
        params.profile_strength = profile.profile_strength;
      }
      prefRef.current = Object.keys(params).length > 0 ? params : undefined;

      try {
        const daily = await fetchDailyQuote(prefRef.current);
        seenIdsRef.current.add(daily.id);
        const more = await fetchRecommend({
          ...(prefRef.current || {}),
          exclude: daily.id,
          limit: '4',
        });
        const fresh = more.filter(q => !seenIdsRef.current.has(q.id));
        fresh.forEach(q => seenIdsRef.current.add(q.id));
        setQuotes([daily, ...fresh]);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    });
  }, [profile]);

  const loadMore = useCallback(async () => {
    if (loadingMoreRef.current) return;
    loadingMoreRef.current = true;
    try {
      const exclude = Array.from(seenIdsRef.current).join(',');
      const more = await fetchRecommend({
        ...(prefRef.current || {}),
        exclude,
        limit: '3',
      });
      const fresh = more.filter(q => !seenIdsRef.current.has(q.id));
      fresh.forEach(q => seenIdsRef.current.add(q.id));
      if (fresh.length > 0) {
        setQuotes(prev => [...prev, ...fresh]);
      }
    } catch (e) {
      console.error(e);
    } finally {
      loadingMoreRef.current = false;
    }
  }, []);

  // swipeCard를 ref로 관리하여 PanResponder 재생성 불필요
  const swipeCard = useCallback((direction: 'left' | 'right') => {
    const toX = direction === 'left' ? -SCREEN_WIDTH * 1.5 : SCREEN_WIDTH * 1.5;

    Animated.timing(position, {
      toValue: {x: toX, y: 0},
      duration: SWIPE_OUT_DURATION,
      useNativeDriver: true,
    }).start(() => {
      // swipeCallbackRef에서 최신 상태 접근
      swipeCallbackRef.current?.(direction);
      position.setValue({x: 0, y: 0});
    });
  }, [position]);

  // 최신 상태를 ref로 유지
  useEffect(() => {
    swipeCallbackRef.current = (direction: 'left' | 'right') => {
      const current = quotes[currentIndex];
      if (current) {
        if (direction === 'left') {
          logInteraction({quote_id: current.id, type: 'like'});
          if (!isFav(current.id)) toggle(current.id);
        } else {
          logInteraction({quote_id: current.id, type: 'unlike'});
        }
        setLastSwiped({quote: current, index: currentIndex});
      }
      if (showHint) {
        setShowHint(false);
        AsyncStorage.setItem(HINT_KEY, 'true');
      }
      setCurrentIndex(prev => {
        const next = prev + 1;
        if (quotes.length - next <= 2) loadMore();
        return next;
      });
    };
  }, [quotes, currentIndex, isFav, toggle, showHint, loadMore]);

  // PanResponder는 한 번만 생성
  const panResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => false,
      onMoveShouldSetPanResponder: (_, gs) => Math.abs(gs.dx) > 10,
      onPanResponderMove: (_, gs) => {
        position.setValue({x: gs.dx, y: gs.dy * 0.3});
      },
      onPanResponderRelease: (_, gs) => {
        if (gs.dx < -SWIPE_THRESHOLD) {
          const toX = -SCREEN_WIDTH * 1.5;
          Animated.timing(position, {
            toValue: {x: toX, y: 0},
            duration: SWIPE_OUT_DURATION,
            useNativeDriver: true,
          }).start(() => {
            swipeCallbackRef.current?.('left');
            position.setValue({x: 0, y: 0});
          });
        } else if (gs.dx > SWIPE_THRESHOLD) {
          const toX = SCREEN_WIDTH * 1.5;
          Animated.timing(position, {
            toValue: {x: toX, y: 0},
            duration: SWIPE_OUT_DURATION,
            useNativeDriver: true,
          }).start(() => {
            swipeCallbackRef.current?.('right');
            position.setValue({x: 0, y: 0});
          });
        } else {
          Animated.spring(position, {
            toValue: {x: 0, y: 0},
            useNativeDriver: true,
            friction: 5,
          }).start();
        }
      },
    }),
  ).current;

  const handleUndo = () => {
    if (!lastSwiped) return;
    setCurrentIndex(lastSwiped.index);
    setLastSwiped(null);
  };

  const currentQuote = quotes[currentIndex];

  const handleShare = async () => {
    if (!currentQuote) return;
    const author = currentQuote.author?.name || '알 수 없음';
    await Share.share({message: `"${currentQuote.text}"\n\n— ${author}`});
    logInteraction({quote_id: currentQuote.id, type: 'share'});
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (quotes.length === 0 || currentIndex >= quotes.length) {
    return (
      <View style={styles.center}>
        <Icon name="checkmark-circle-outline" size={48} color={colors.textMuted} />
        <Text style={styles.emptyText}>모든 명언을 확인했습니다</Text>
        <TouchableOpacity
          style={styles.reloadBtn}
          onPress={() => {
            setLoading(true);
            seenIdsRef.current.clear();
            setQuotes([]);
            setCurrentIndex(0);
            getPreference().then(async pref => {
              const params: Record<string, string> = {};
              if (pref) {
                params.situations = pref.situation_groups.join(',');
                params.keywords = pref.keyword_groups.join(',');
              }
              prefRef.current = Object.keys(params).length > 0 ? params : undefined;
              try {
                const daily = await fetchDailyQuote(prefRef.current);
                seenIdsRef.current.add(daily.id);
                const more = await fetchRecommend({
                  ...(prefRef.current || {}),
                  exclude: daily.id,
                  limit: '4',
                });
                const fresh = more.filter(q => !seenIdsRef.current.has(q.id));
                fresh.forEach(q => seenIdsRef.current.add(q.id));
                setQuotes([daily, ...fresh]);
              } catch {} finally {
                setLoading(false);
              }
            });
          }}>
          <Text style={styles.reloadText}>새로운 명언 불러오기</Text>
        </TouchableOpacity>
      </View>
    );
  }

  // 애니메이션 보간
  const rotate = position.x.interpolate({
    inputRange: [-SCREEN_WIDTH, 0, SCREEN_WIDTH],
    outputRange: ['-12deg', '0deg', '12deg'],
  });

  const likeOpacity = position.x.interpolate({
    inputRange: [-SCREEN_WIDTH / 2, -SWIPE_THRESHOLD / 2, 0],
    outputRange: [1, 0.8, 0],
    extrapolate: 'clamp',
  });

  const nopeOpacity = position.x.interpolate({
    inputRange: [0, SWIPE_THRESHOLD / 2, SCREEN_WIDTH / 2],
    outputRange: [0, 0.8, 1],
    extrapolate: 'clamp',
  });

  const renderCards = () => {
    return quotes
      .slice(currentIndex, currentIndex + 3)
      .map((quote, i) => {
        const isTop = i === 0;
        const stackScale = 1 - i * 0.05;
        const stackTop = i * 8;

        if (isTop) {
          return (
            <Animated.View
              key={quote.id}
              style={[
                styles.card,
                styles.cardTop,
                {
                  transform: [
                    {translateX: position.x},
                    {translateY: position.y},
                    {rotate},
                  ],
                },
              ]}
              {...panResponder.panHandlers}>
              {/* LIKE 스탬프 */}
              <Animated.View style={[styles.stamp, styles.likeStamp, {opacity: likeOpacity}]}>
                <Text style={styles.likeStampText}>LIKE</Text>
              </Animated.View>

              {/* NOPE 스탬프 */}
              <Animated.View style={[styles.stamp, styles.nopeStamp, {opacity: nopeOpacity}]}>
                <Text style={styles.nopeStampText}>NOPE</Text>
              </Animated.View>

              <TouchableOpacity
                activeOpacity={0.9}
                onPress={() => navigation.navigate('QuoteDetail', {quoteId: quote.id})}
                style={styles.cardContent}>
                <Text style={styles.quoteText}>"{quote.text}"</Text>
                {quote.text_original && quote.text_original !== quote.text && (
                  <Text style={styles.originalText}>{quote.text_original}</Text>
                )}
                <Text style={styles.authorName}>— {quote.author?.name}</Text>
                {quote.author?.profession && (
                  <Text style={styles.profession}>{quote.author.profession}</Text>
                )}
                {quote.keywords && quote.keywords.length > 0 && (
                  <View style={styles.tags}>
                    {quote.keywords.slice(0, 4).map(k => (
                      <View key={k} style={styles.tag}>
                        <Text style={styles.tagText}>#{k}</Text>
                      </View>
                    ))}
                  </View>
                )}
              </TouchableOpacity>
            </Animated.View>
          );
        }

        return (
          <View
            key={quote.id}
            style={[
              styles.card,
              {
                top: stackTop,
                transform: [{scale: stackScale}],
                zIndex: -i,
              },
            ]}>
            <View style={styles.cardContent}>
              <Text style={styles.quoteText} numberOfLines={4}>"{quote.text}"</Text>
              <Text style={styles.authorName}>— {quote.author?.name}</Text>
            </View>
          </View>
        );
      })
      .reverse();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>
        {currentIndex === 0 ? '오늘의 명언' : '추천 명언'}
      </Text>

      <View style={styles.cardContainer}>
        {renderCards()}

        {/* 힌트 오버레이 — 탭하면 사라짐 */}
        {showHint && (
          <TouchableOpacity
            activeOpacity={1}
            onPress={() => {
              setShowHint(false);
              AsyncStorage.setItem(HINT_KEY, 'true');
              hintOpacity.setValue(0);
            }}
            style={StyleSheet.absoluteFill}>
            <Animated.View style={[styles.hintOverlay, {opacity: hintOpacity}]}>
              <View style={styles.hintContent}>
                <View style={styles.hintSide}>
                  <Icon name="heart" size={28} color={colors.success} />
                  <Text style={styles.hintLabel}>좋아요</Text>
                </View>
                <Text style={styles.hintArrowLeft}>{'<'} 밀기</Text>
                <View style={styles.hintDivider} />
                <Text style={styles.hintArrowRight}>밀기 {'>'}</Text>
                <View style={styles.hintSide}>
                  <Icon name="close-circle" size={28} color={colors.heart} />
                  <Text style={styles.hintLabel}>별로예요</Text>
                </View>
              </View>
              <Text style={styles.hintDismiss}>탭하여 닫기</Text>
            </Animated.View>
          </TouchableOpacity>
        )}
      </View>

      {/* 하단 보조 버튼 */}
      <View style={styles.bottomActions}>
        <TouchableOpacity
          style={[styles.bottomBtn, !lastSwiped && styles.bottomBtnDisabled]}
          onPress={handleUndo}
          disabled={!lastSwiped}>
          <Icon name="arrow-undo-outline" size={22} color={lastSwiped ? colors.warning : colors.textMuted} />
        </TouchableOpacity>
        <TouchableOpacity style={styles.bottomBtn} onPress={handleShare}>
          <Icon name="share-outline" size={22} color={colors.textSecondary} />
        </TouchableOpacity>
        <TouchableOpacity
          style={styles.bottomBtn}
          onPress={() => currentQuote && navigation.navigate('QuoteDetail', {quoteId: currentQuote.id})}>
          <Icon name="information-circle-outline" size={22} color={colors.textSecondary} />
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
    paddingTop: 60,
  },
  center: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: colors.background,
  },
  emptyText: {
    color: colors.textMuted,
    fontSize: 16,
    marginTop: 16,
  },
  reloadBtn: {
    marginTop: 24,
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  reloadText: {
    color: colors.background,
    fontSize: 14,
    fontWeight: '600',
  },
  errorText: {color: colors.textSecondary, fontSize: 16},
  label: {
    color: colors.textMuted,
    fontSize: 14,
    textAlign: 'center',
    marginBottom: 16,
    letterSpacing: 2,
    textTransform: 'uppercase',
  },

  // 카드 컨테이너
  cardContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  card: {
    position: 'absolute',
    width: SCREEN_WIDTH - 40,
    minHeight: CARD_HEIGHT,
    backgroundColor: colors.surface,
    borderRadius: 24,
    shadowColor: '#000',
    shadowOffset: {width: 0, height: 8},
    shadowOpacity: 0.3,
    shadowRadius: 16,
    elevation: 12,
    overflow: 'hidden',
  },
  cardTop: {
    zIndex: 10,
  },
  cardContent: {
    flex: 1,
    padding: 32,
    justifyContent: 'center',
    alignItems: 'center',
  },

  // 스탬프
  stamp: {
    position: 'absolute',
    zIndex: 20,
    borderWidth: 3,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  likeStamp: {
    top: 28,
    left: 24,
    borderColor: colors.success,
    transform: [{rotate: '-15deg'}],
  },
  likeStampText: {
    color: colors.success,
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: 3,
  },
  nopeStamp: {
    top: 28,
    right: 24,
    borderColor: colors.heart,
    transform: [{rotate: '15deg'}],
  },
  nopeStampText: {
    color: colors.heart,
    fontSize: 28,
    fontWeight: '800',
    letterSpacing: 3,
  },

  // 카드 내용
  quoteText: {
    color: colors.text,
    fontSize: 20,
    lineHeight: 34,
    textAlign: 'center',
    fontWeight: '300',
    letterSpacing: 0.3,
  },
  originalText: {
    color: colors.textMuted,
    fontSize: 13,
    textAlign: 'center',
    marginTop: 12,
    fontStyle: 'italic',
  },
  authorName: {
    color: colors.primary,
    fontSize: 15,
    fontWeight: '600',
    marginTop: 24,
  },
  profession: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: 4,
  },
  tags: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'center',
    gap: 6,
    marginTop: 20,
  },
  tag: {
    backgroundColor: 'rgba(56, 189, 248, 0.1)',
    borderRadius: 12,
    paddingHorizontal: 10,
    paddingVertical: 4,
  },
  tagText: {
    color: colors.primary,
    fontSize: 12,
    fontWeight: '500',
  },

  // 힌트 오버레이
  hintOverlay: {
    position: 'absolute',
    top: 0,
    left: 20,
    right: 20,
    bottom: 0,
    backgroundColor: 'rgba(15, 23, 42, 0.88)',
    borderRadius: 24,
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 30,
  },
  hintContent: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  hintSide: {
    alignItems: 'center',
    gap: 8,
  },
  hintArrowLeft: {
    color: colors.success,
    fontSize: 16,
    fontWeight: '600',
  },
  hintArrowRight: {
    color: colors.heart,
    fontSize: 16,
    fontWeight: '600',
  },
  hintLabel: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '600',
  },
  hintDivider: {
    width: 1,
    height: 60,
    backgroundColor: colors.surfaceLight,
  },
  hintDismiss: {
    color: colors.textMuted,
    fontSize: 12,
    marginTop: 24,
  },

  // 하단 버튼
  bottomActions: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 32,
    paddingBottom: 24,
    paddingTop: 16,
  },
  bottomBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.surfaceLight,
    justifyContent: 'center',
    alignItems: 'center',
  },
  bottomBtnDisabled: {
    opacity: 0.4,
  },
});
