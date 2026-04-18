import React, {useEffect, useState} from 'react';
import {View, Text, TouchableOpacity, StyleSheet, ActivityIndicator, Share} from 'react-native';
import {colors} from '../constants/colors';
import {fetchDailyQuote} from '../api/client';
import {useFavorites} from '../hooks/useFavorites';
import {getPreference} from '../storage/preferences';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';

export function HomeScreen({navigation}: {navigation: NativeStackNavigationProp<any>}) {
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const {toggle, isFav} = useFavorites();

  useEffect(() => {
    getPreference().then(pref => {
      const params = pref
        ? {
            situations: pref.situation_groups.join(','),
            keywords: pref.keyword_groups.join(','),
          }
        : undefined;
      return fetchDailyQuote(params);
    })
      .then(setQuote)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const handleShare = async () => {
    if (!quote) return;
    const author = quote.author?.name || '알 수 없음';
    await Share.share({message: `"${quote.text}"\n\n— ${author}`});
  };

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color={colors.primary} />
      </View>
    );
  }

  if (!quote) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>명언을 불러올 수 없습니다.</Text>
      </View>
    );
  }

  const fav = isFav(quote.id);

  return (
    <View style={styles.container}>
      <Text style={styles.label}>오늘의 명언</Text>

      <TouchableOpacity
        style={styles.quoteArea}
        activeOpacity={0.8}
        onPress={() => navigation.navigate('QuoteDetail', {quoteId: quote.id})}>
        <Text style={styles.quoteText}>"{quote.text}"</Text>
        {quote.text_original && quote.text_original !== quote.text && (
          <Text style={styles.originalText}>{quote.text_original}</Text>
        )}
        <Text style={styles.author}>— {quote.author?.name}</Text>
        {quote.author?.profession && (
          <Text style={styles.profession}>{quote.author.profession}</Text>
        )}
      </TouchableOpacity>

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => toggle(quote.id)}>
          <Text style={[styles.actionIcon, fav && {color: colors.heart}]}>
            {fav ? '♥' : '♡'}
          </Text>
          <Text style={styles.actionLabel}>좋아요</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={handleShare}>
          <Text style={styles.actionIcon}>↗</Text>
          <Text style={styles.actionLabel}>공유</Text>
        </TouchableOpacity>
      </View>

      {quote.keywords && quote.keywords.length > 0 && (
        <View style={styles.tags}>
          {quote.keywords.map(k => (
            <View key={k} style={styles.tag}>
              <Text style={styles.tagText}>#{k}</Text>
            </View>
          ))}
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background, justifyContent: 'center', padding: 24},
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
});
