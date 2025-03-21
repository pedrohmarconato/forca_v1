import React from 'react';
import logo from './logo.svg';
import './App.css';
import Questionario from './components/Questionario';

function App() {
  // Usando o componente Questionario em vez do conteúdo padrão
  return (
    <div className="App">
      <Questionario />
    </div>
  );
}

export default App;
