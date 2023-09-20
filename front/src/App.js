import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Main from './Main';
import Admin from './Admin';
import Sub1 from './Sub1';
import Sub2 from './Sub2';


const App = () => {
	return (
		<div className='App'>
			<BrowserRouter>
				<Routes>
					<Route path="/" exact element={<Main />}></Route>
					<Route path="/subpage" exact element={<Sub1 />}></Route>
                    <Route path="/admin" exact element={<Admin />}></Route>
                    <Route path="/contents" exact element={<Sub2 />}></Route>
				</Routes>
			</BrowserRouter>
		</div>
    
	);
};

export default App;