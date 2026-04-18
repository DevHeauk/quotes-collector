import React, {useState} from 'react';
import {View, Text, TouchableOpacity, StyleSheet} from 'react-native';
import {SafeAreaView} from 'react-native-safe-area-context';
import {colors} from '../../constants/colors';
import type {NativeStackScreenProps} from '@react-navigation/native-stack';
import type {OnboardingStackParamList} from '../../types/navigation';

const SITUATIONS = [
  {key: '위기/고난', emoji: '🌊', desc: '힘들고 지칠 때'},
  {key: '성장/도전', emoji: '🚀', desc: '새로운 도전 앞에서'},
  {key: '관계', emoji: '💬', desc: '사람 사이에서 고민될 때'},
  {key: '자기성찰', emoji: '🪞', desc: '나를 돌아보고 싶을 때'},
  {key: '일/학업', emoji: '📚', desc: '일이나 공부에 집중할 때'},
  {key: '일상', emoji: '☕', desc: '평범한 하루에 영감이 필요할 때'},
];

type Props = NativeStackScreenProps<OnboardingStackParamList, 'SituationPicker'>;

export function SituationPickerScreen({navigation}: Props) {
  const [selected, setSelected] = useState<string[]>([]);

  const toggle = (key: string) => {
    setSelected(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : prev.length < 3 ? [...prev, key] : prev,
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.step}>1 / 3</Text>
        <Text style={styles.title}>지금 어떤 상황인가요?</Text>
        <Text style={styles.subtitle}>관심 있는 상황을 골라주세요 (최대 3개)</Text>
      </View>

      <View style={styles.grid}>
        {SITUATIONS.map(s => {
          const active = selected.includes(s.key);
          return (
            <TouchableOpacity
              key={s.key}
              style={[styles.card, active && styles.cardActive]}
              onPress={() => toggle(s.key)}
              activeOpacity={0.7}>
              <Text style={styles.emoji}>{s.emoji}</Text>
              <Text style={[styles.cardTitle, active && styles.cardTitleActive]}>{s.key}</Text>
              <Text style={styles.cardDesc}>{s.desc}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      <TouchableOpacity
        style={[styles.nextBtn, selected.length === 0 && styles.nextBtnDisabled]}
        disabled={selected.length === 0}
        onPress={() => navigation.navigate('KeywordPicker', {situations: selected})}>
        <Text style={styles.nextText}>다음</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {flex: 1, backgroundColor: colors.background, padding: 24},
  header: {marginTop: 20, marginBottom: 32},
  step: {color: colors.primary, fontSize: 14, fontWeight: '600', marginBottom: 8},
  title: {color: colors.text, fontSize: 24, fontWeight: '700', marginBottom: 8},
  subtitle: {color: colors.textMuted, fontSize: 14},
  grid: {flexDirection: 'row', flexWrap: 'wrap', gap: 12},
  card: {
    width: '47%',
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 20,
    borderWidth: 2,
    borderColor: 'transparent',
  },
  cardActive: {borderColor: colors.primary, backgroundColor: '#1e3a5f'},
  emoji: {fontSize: 28, marginBottom: 8},
  cardTitle: {color: colors.text, fontSize: 16, fontWeight: '600', marginBottom: 4},
  cardTitleActive: {color: colors.primary},
  cardDesc: {color: colors.textMuted, fontSize: 12, lineHeight: 18},
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
