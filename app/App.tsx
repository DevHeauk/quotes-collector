import React, {useEffect, useState} from 'react';
import {StatusBar, ActivityIndicator, View} from 'react-native';
import {NavigationContainer} from '@react-navigation/native';
import {SafeAreaProvider} from 'react-native-safe-area-context';
import {createNativeStackNavigator} from '@react-navigation/native-stack';
import {RootNavigator} from './src/navigation/RootNavigator';
import {SituationPickerScreen} from './src/screens/onboarding/SituationPickerScreen';
import {KeywordPickerScreen} from './src/screens/onboarding/KeywordPickerScreen';
import {QuoteTasteScreen} from './src/screens/onboarding/QuoteTasteScreen';
import {isOnboardingCompleted} from './src/storage/preferences';
import type {OnboardingStackParamList} from './src/types/navigation';

const Stack = createNativeStackNavigator<OnboardingStackParamList>();

function App() {
  const [ready, setReady] = useState(false);
  const [onboarded, setOnboarded] = useState(false);

  useEffect(() => {
    isOnboardingCompleted().then(done => {
      setOnboarded(done);
      setReady(true);
    });
  }, []);

  if (!ready) {
    return (
      <View style={{flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0f172a'}}>
        <ActivityIndicator size="large" color="#38bdf8" />
      </View>
    );
  }

  return (
    <SafeAreaProvider>
      <StatusBar barStyle="light-content" backgroundColor="#0f172a" />
      <NavigationContainer>
        <Stack.Navigator
          screenOptions={{headerShown: false}}
          initialRouteName={onboarded ? 'Main' : 'SituationPicker'}>
          <Stack.Screen name="SituationPicker" component={SituationPickerScreen} />
          <Stack.Screen name="KeywordPicker" component={KeywordPickerScreen} />
          <Stack.Screen name="QuoteTaste" component={QuoteTasteScreen} />
          <Stack.Screen name="Main" component={RootNavigator} />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}

export default App;
