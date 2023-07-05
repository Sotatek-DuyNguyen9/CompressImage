import './App.scss';
import Header from './components/header';
import Homepage from './pages/homepage';
import TestComponent from './pages/test';

function App() {
  return (
    <div style={{ backgroundColor: "#f5f5f5", minHeight:"100vh" }}> 
      <Header />
      <Homepage /> 
      {/* <TestComponent /> */}
    </div>
  );
}

export default App;
