import React, {useEffect, useState} from 'react';
import {View, Text, ScrollView, TouchableOpacity, StyleSheet, ActivityIndicator, Share} from 'react-native';
import {colors} from '../constants/colors';
import {fetchQuoteDetail} from '../api/client';
import {useFavorites} from '../hooks/useFavorites';
import {logInteraction} from '../storage/interactions';
import type {Quote} from '../types';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';
import type {RouteProp} from '@react-navigation/native';

type Props = {
  navigation: NativeStackNavigationProp<any>;
  route: RouteProp<{QuoteDetail: {quoteId: string}}, 'QuoteDetail'>;
};

export function QuoteDetailScreen({navigation, route}: Props) {
  const {quoteId} = route.params;
  const [quote, setQuote] = useState<Quote | null>(null);
  const [loading, setLoading] = useState(true);
  const {toggle, isFav} = useFavorites();

  useEffect(() => {
    logInteraction({quote_id: quoteId, type: 'view_detail'});
    fetchQuoteDetail(quoteId)
      .then(setQuote)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, [quoteId]);

  if (loading) {
    return <View style={styles.center}><ActivityIndicator size="large" color={colors.primary} /></View>;
  }
  if (!quote) {
    return <View style={styles.center}><Text style={styles.errorText}>명언을 찾을 수 없습니다.</Text></View>;
  }

  const fav = isFav(quote.id);
  const author = quote.author;

  const handleShare = async () => {
    await Share.share({message: `"${quote.text}"\n\n— ${author?.name || '알 수 없음'}`});
    logInteraction({quote_id: quote.id, type: 'share'});
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <Text style={styles.quoteText}>"{quote.text}"</Text>

      {quote.text_original && quote.text_original !== quote.text && (
        <Text style={styles.original}>{quote.text_original}</Text>
      )}

      <View style={styles.authorSection}>
        <Text style={styles.authorName}>{author?.name}</Text>
        <Text style={styles.authorInfo}>
          {[author?.profession, author?.field, author?.nationality].filter(Boolean).join(' · ')}
          {author?.birth_year ? ` · ${author.birth_year < 0 ? `BC ${Math.abs(author.birth_year)}` : author.birth_year}` : ''}
        </Text>
      </View>

      {quote.source && <Text style={styles.source}>출처: {quote.source}</Text>}

      <View style={styles.actions}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => toggle(quote.id)}>
          <Text style={[styles.actionIcon, fav && {color: colors.heart}]}>{fav ? '♥' : '♡'}</Text>
          <Text style={styles.actionLabel}>좋아요</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={handleShare}>
          <Text style={styles.actionIcon}>↗</Text>
          <Text style={styles.actionLabel}>공유</Text>
        </TouchableOpacity>
      </View>

      {quote.keywords && quote.keywords.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>키워드</Text>
          <View style={styles.tags}>
            {quote.keywords.map(k => (
              <View key={k} style={styles.tag}><Text style={styles.tagText}>#{k}</Text></View>
            ))}
          </View>
        </View>
      )}

      {quote.situations && quote.situations.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>이럴 때 읽기 좋아요</Text>
          <View style={styles.tags}>
            {quote.situations.map(s => (
              <View key={s} style={styles.tag}><Text style={styles.tagText}>{s}</Text></View>
            ))}
          </View>
        </View>
      )}

      {quote.related_quotes && quote.related_quotes.length > 0 && (
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>같은 저자의 명언</Text>
          {quote.related_quotes.map(rq => (
            <TouchableOpacity
              key={rq.id}
              style={styles.relatedItem}
              onPress={() => navigation.push('QuoteDetail', {quoteId: rq.id})}>
              <Text style={styles.relatedText} numberOfLines={2}>"{rq.text}"</Text>
            </TouchableOpacity>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background},
  content: {padding: 24},
  center: {flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: colors.background},
  errorText: {color: colors.textSecondary, fontSize: 16},
  quoteText: {color: colors.text, fontSize: 22, lineHeight: 36, fontWeight: '300'},
  original: {color: colors.textMuted, fontSize: 14, marginTop: 16, fontStyle: 'italic'},
  authorSection: {marginTop: 24, paddingTop: 20, borderTopWidth: 1, borderTopColor: colors.border},
  authorName: {color: colors.primary, fontSize: 18, fontWeight: '600'},
  authorInfo: {color: colors.textMuted, fontSize: 13, marginTop: 4},
  source: {color: colors.textMuted, fontSize: 13, marginTop: 12},
  actions: {flexDirection: 'row', gap: 32, marginTop: 24},
  actionBtn: {alignItems: 'center'},
  actionIcon: {fontSize: 28, color: colors.textSecondary},
  actionLabel: {color: colors.textMuted, fontSize: 12, marginTop: 4},
  section: {marginTop: 28},
  sectionTitle: {color: colors.textMuted, fontSize: 13, marginBottom: 10, textTransform: 'uppercase', letterSpacing: 1},
  tags: {flexDirection: 'row', flexWrap: 'wrap', gap: 8},
  tag: {backgroundColor: colors.surfaceLight, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6},
  tagText: {color: colors.textSecondary, fontSize: 13},
  relatedItem: {paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: colors.border},
  relatedText: {color: colors.text, fontSize: 14, lineHeight: 22},
});
