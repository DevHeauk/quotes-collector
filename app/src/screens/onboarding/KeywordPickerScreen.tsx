import React, {useState} from 'react';
import {View, Text, TouchableOpacity, StyleSheet} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {colors} from '../../constants/colors';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {OnboardingStackParamList} from '../../types/navigation';

const KEYWORDS = [
  {key: '감정', emoji: '💛', desc: '감정과 마음에 대한'},
  {key: '가치관', emoji: '⚖️', desc: '삶의 기준과 철학'},
  {key: '행동/태도', emoji: '🔥', desc: '실천과 의지에 대한'},
  {key: '관계', emoji: '🤝', desc: '사람과의 연결'},
  {key: '지성', emoji: '🧠', desc: '지식과 사고에 대한'},
  {key: '인생', emoji: '🌱', desc: '삶 전반에 대한 통찰'},
  {key: '사회', emoji: '🌍', desc: '세상과 사회에 대한'},
  {key: '자연/과학', emoji: '🔬', desc: '자연과 과학의 지혜'},
  {key: '유머/표현', emoji: '😄', desc: '위트 있는 한마디'},
];

type Props = NativeStackScreenProps<OnboardingStackParamList, 'KeywordPicker'>;

export function KeywordPickerScreen({navigation, route}: Props) {
  const [selected, setSelected] = useState<string[]>([]);
  const {situations} = route.params;

  const toggle = (key: string) => {
    setSelected(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : prev.length < 3 ? [...prev, key] : prev,
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.step}>2 / 3</Text>
        <Text style={styles.title}>어떤 주제의 명언을 좋아하세요?</Text>
        <Text style={styles.subtitle}>관심 있는 주제를 골라주세요 (최대 3개)</Text>
      </View>

      <View style={styles.grid}>
        {KEYWORDS.map(k => {
          const active = selected.includes(k.key);
          return (
            <TouchableOpacity
              key={k.key}
              style={[styles.card, active && styles.cardActive]}
              onPress={() => toggle(k.key)}
              activeOpacity={0.7}>
              <Text style={styles.emoji}>{k.emoji}</Text>
              <Text style={[styles.cardTitle, active && styles.cardTitleActive]}>{k.key}</Text>
              <Text style={styles.cardDesc}>{k.desc}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity
        style={[styles.nextBtn, selected.length === 0 && styles.nextBtnDisabled]}
        disabled={selected.length === 0}
        onPress={() => navigation.navigate('QuoteTaste', {situations, keywords: selected})}>
        <Text style={styles.nextText}>다음</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background, padding: 24},
  header: {marginTop: 20, marginBottom: 24},
  step: {color: colors.primary, fontSize: 14, fontWeight: '600', marginBottom: 8},
  title: {color: colors.text, fontSize: 24, fontWeight: '700', marginBottom: 8},
  subtitle: {color: colors.textMuted, fontSize: 14},
  grid: {flexDirection: 'row', flexWrap: 'wrap', gap: 12},
  card: {
    width: '30%',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 14,
    borderWidth: 2,
    borderColor: 'transparent',
    alignItems: 'center',
  },
  cardActive: {borderColor: colors.primary, backgroundColor: '#1e3a5f'},
  emoji: {fontSize: 24, marginBottom: 6},
  cardTitle: {color: colors.text, fontSize: 13, fontWeight: '600', marginBottom: 2, textAlign: 'center'},
  cardTitleActive: {color: colors.primary},
  cardDesc: {color: colors.textMuted, fontSize: 10, textAlign: 'center', lineHeight: 14},
  nextBtn: {
    position: 'absolute',
    bottom: 40,
    left: 24,
    right: 24,
    backgroundColor: colors.primary,
    borderRadius: 14,
    paddingVertical: 16,
    alignItems: 'center',
  },
  nextBtnDisabled: {backgroundColor: colors.surfaceLight, opacity: 0.5},
  nextText: {color: colors.background, fontSize: 16, fontWeight: '700'},
});
