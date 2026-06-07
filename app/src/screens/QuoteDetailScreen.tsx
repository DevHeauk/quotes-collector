import React from 'react';
import {ResponsiveContainer} from '../components/ResponsiveContainer';
import {QuoteDetailView} from '../components/QuoteDetailView';
import type {NativeStackNavigationProp} from '@react-navigation/native-stack';
import type {RouteProp} from '@react-navigation/native';

type Props = {
  navigation: NativeStackNavigationProp<any>;
  route: RouteProp<{QuoteDetail: {quoteId: string}}, 'QuoteDetail'>;
};

export function QuoteDetailScreen({navigation, route}: Props) {
  const {quoteId} = route.params;
  return (
    <ResponsiveContainer>
      <QuoteDetailView
        quoteId={quoteId}
        onNavigateToQuote={id => navigation.push('QuoteDetail', {quoteId: id})}
        onAfterDelete={() => navigation.goBack()}
      />
    </ResponsiveContainer>
  );
}
