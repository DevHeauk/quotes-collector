import React from 'react';
import {createBottomTabNavigator} from '@react-navigation/bottom-tabs';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {Text} from 'react-native';
import {colors} from '../constants/colors';

import {HomeScreen} from '../screens/HomeScreen';
import {ExploreScreen} from '../screens/ExploreScreen';
import {QuoteListScreen} from '../screens/QuoteListScreen';
import {QuoteDetailScreen} from '../screens/QuoteDetailScreen';
import {FavoritesScreen} from '../screens/FavoritesScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const stackScreenOptions = {
  headerStyle: {backgroundColor: colors.background},
  headerTintColor: colors.text,
  headerTitleStyle: {fontSize: 16},
};

function HomeStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="HomeMain" component={HomeScreen} options={{headerShown: false}} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function ExploreStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="ExploreMain" component={ExploreScreen} options={{title: '탐색'}} />
      <Stack.Screen name="QuoteList" component={QuoteListScreen} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function FavoritesStack() {
  return (
    <Stack.Navigator screenOptions={stackScreenOptions}>
      <Stack.Screen name="FavoritesMain" component={FavoritesScreen} options={{title: '좋아요'}} />
      <Stack.Screen name="QuoteDetail" component={QuoteDetailScreen} options={{title: '명언 상세'}} />
    </Stack.Navigator>
  );
}

function TabIcon({label, focused}: {label: string; focused: boolean}) {
  const icons: Record<string, string> = {'홈': '◉', '탐색': '◎', '좋아요': '♥'};
  return (
    <Text style={{fontSize: 20, color: focused ? colors.primary : colors.textMuted}}>
      {icons[label] || '•'}
    </Text>
  );
}

export function RootNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({route}) => ({
        headerShown: false,
        tabBarStyle: {backgroundColor: colors.background, borderTopColor: colors.border},
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: colors.textMuted,
        tabBarIcon: ({focused}) => <TabIcon label={route.name} focused={focused} />,
      })}>
      <Tab.Screen name="홈" component={HomeStack} />
      <Tab.Screen name="탐색" component={ExploreStack} />
      <Tab.Screen name="좋아요" component={FavoritesStack} />
    </Tab.Navigator>
  );
}
