import React from 'react';

function FilterBar({ filters, selectedFilterId, onFilterSelect, onLutUploadClick, isActive }) {
  return (
    <footer id="filter-bar" className={isActive ? 'active' : ''}>
      <div id="upload-filter-box" className="filter-swatch" onClick={onLutUploadClick}>
        <i className="fas fa-plus"></i>
        <span>Upload LUT</span>
      </div>
      <div id="preset-filter-list">
        {filters.map(filter => (
          <div
            key={filter.id}
            className={`filter-swatch ${selectedFilterId === filter.id ? 'selected' : ''}`}
            onClick={() => onFilterSelect(filter.id)}
          >
            <span>{filter.filter_name || filter.name}</span>
          </div>
        ))}
      </div>
    </footer>
  );
}

export default FilterBar;