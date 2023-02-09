import React from 'react';
import PropTypes from 'prop-types';

export const StoreContext = React.createContext(null)

const StoreProvider = ({ children }) => {
  const [showLogout, setShowLogout] = React.useState(0);
  const [pagelocation, setPageLocation] = React.useState();

  const store = {
    showLogout: [showLogout, setShowLogout],
    pagelocation: [pagelocation, setPageLocation]
  }

  return <StoreContext.Provider value={store}>{children}</StoreContext.Provider>
}

StoreProvider.propTypes = {
  children: PropTypes.any
}

export default StoreProvider;
