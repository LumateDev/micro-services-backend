import { useState } from "react";
import axios from "axios";
import { SHA256 } from "crypto-js";
import Home from "./Home.js";

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const [registrationData, setRegistrationData] = useState({
    email: "",
    password: "",
  });

  const [loginData, setLoginData] = useState({
    email: "",
    password: "",
  });

  const handleRegistrationChange = (e) => {
    const { name, value } = e.target;
    setRegistrationData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const handleLoginChange = (e) => {
    const { name, value } = e.target;
    setLoginData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };

  const sendRegistrationData = async (data) => {
    try {
      const hashedPassword = SHA256(data.password).toString();
      const response = await axios.post("http://127.0.0.1:8000/registration", {
        email: data.email,
        password: hashedPassword,
      });
      if (response.status === 200) {
        alert(response.data.message);
        setIsAuthenticated(true);
      } else if (response.status === 202) {
        alert(response.data.message);
      }
    } catch (error) {
      console.error("Ошибка регистрации:", error);
      alert("Ошибка регистрации. Попробуйте снова.");
    }
  };

  const sendLoginData = async (data) => {
    try {
      const hashedPassword = SHA256(data.password).toString();
      const response = await axios.post("http://127.0.0.1:8000/authorization", {
        email: data.email,
        password: hashedPassword,
      });
      if (response.status === 200) {
        alert(response.data.message);
        setIsAuthenticated(true);
      } else if (response.status === 202) {
        alert(response.data.message);
      }
    } catch (error) {
      console.error("Ошибка авторизации:", error);
      alert("Ошибка авторизации. Попробуйте снова.");
    }
  };

  const handleRegistrationSubmit = (e) => {
    e.preventDefault();
    sendRegistrationData(registrationData);
  };

  const handleLoginSubmit = (e) => {
    e.preventDefault();
    sendLoginData(loginData);
  };

  return (
    <div>
      {isAuthenticated === false ? (
        <div>
          <div>
            <h3>Регистрация</h3>
            <form onSubmit={handleRegistrationSubmit}>
              <input
                type="email"
                name="email"
                placeholder="Введите email"
                value={registrationData.email}
                onChange={handleRegistrationChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Введите пароль"
                value={registrationData.password}
                onChange={handleRegistrationChange}
              />
              <button type="submit">Зарегистрироваться</button>
            </form>
          </div>
          <div>
            <h3>Авторизация</h3>
            <form onSubmit={handleLoginSubmit}>
              <input
                type="email"
                name="email"
                placeholder="Введите email"
                value={loginData.email}
                onChange={handleLoginChange}
              />
              <input
                type="password"
                name="password"
                placeholder="Введите пароль"
                value={loginData.password}
                onChange={handleLoginChange}
              />
              <button type="submit">Авторизоваться</button>
            </form>
          </div>
        </div>
      ) : (
        <Home />
      )}
    </div>
  );
}

export default App;
