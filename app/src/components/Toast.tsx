import React, {useEffect, useRef} from 'react';
import {Animated, Text, StyleSheet} from 'react-native';
import {colors} from '../constants/colors';

interface Props {
  message: string;
  visible: boolean;
  onHide: () => void;
  duration?: number;
}

export function Toast({message, visible, onHide, duration = 2500}: Props) {
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    if (visible) {
      Animated.sequence([
        Animated.timing(opacity, {toValue: 1, duration: 300, useNativeDriver: true}),
        Animated.delay(duration),
        Animated.timing(opacity, {toValue: 0, duration: 300, useNativeDriver: true}),
      ]).start(() => onHide());
    }
  }, [visible, opacity, duration, onHide]);

  if (!visible) return null;

  return (
    <Animated.View style={[styles.container, {opacity}]}>
      <Text style={styles.text}>{message}</Text>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: 'absolute',
    bottom: 100,
    alignSelf: 'center',
    backgroundColor: colors.surfaceLight,
    borderRadius: 20,
    paddingHorizontal: 20,
    paddingVertical: 10,
  },
  text: {
    color: colors.text,
    fontSize: 14,
    fontWeight: '500',
  },
});
