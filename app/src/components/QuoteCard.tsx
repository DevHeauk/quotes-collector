import React from 'react';
import {View, Text, TouchableOpacity, StyleSheet} from 'react-native';
import {colors} from '../constants/colors';
import type {Quote} from '../types';

interface Props {
  quote: Quote;
  isFavorite: boolean;
  onPress: () => void;
  onToggleFavorite: () => void;
}

export function QuoteCard({quote, isFavorite, onPress, onToggleFavorite}: Props) {
  const authorName = quote.author?.name || quote.author_name || '알 수 없음';
  return (
    <TouchableOpacity style={styles.card} onPress={onPress} activeOpacity={0.7}>
      <Text style={styles.text} numberOfLines={4}>
        "{quote.text}"
      </Text>
      <View style={styles.bottom}>
        <Text style={styles.author}>— {authorName}</Text>
        <TouchableOpacity onPress={onToggleFavorite} hitSlop={{top: 10, bottom: 10, left: 10, right: 10}}>
          <Text style={[styles.heart, isFavorite && styles.heartActive]}>
            {isFavorite ? '♥' : '♡'}
          </Text>
        </TouchableOpacity>
      </View>
      {quote.keywords && quote.keywords.length > 0 && (
        <View style={styles.tags}>
          {quote.keywords.slice(0, 3).map(k => (
            <View key={k} style={styles.tag}>
              <Text style={styles.tagText}>#{k}</Text>
            </View>
          ))}
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 20,
    marginHorizontal: 16,
    marginVertical: 8,
  },
  text: {
    color: colors.text,
    fontSize: 16,
    lineHeight: 26,
    fontWeight: '400',
  },
  bottom: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 12,
  },
  author: {
    color: colors.textSecondary,
    fontSize: 14,
  },
  heart: {
    fontSize: 24,
    color: colors.heartInactive,
  },
  heartActive: {
    color: colors.heart,
  },
  tags: {
    flexDirection: 'row',
    marginTop: 10,
    gap: 6,
  },
  tag: {
    backgroundColor: colors.surfaceLight,
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  tagText: {
    color: colors.textMuted,
    fontSize: 12,
  },
});
