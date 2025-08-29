import React from 'react';

function FilterBar({ 
  filters, 
  selectedFilterId, 
  onFilterSelect, 
  onLutUploadClick, 
  isActive,
  currentPage,
  totalItems,
  itemsPerPage,
  onPageChange
}) {

  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <footer id="filter-bar" className={isActive ? 'active' : ''}>
      <div className="filter-scroll-container">

        {/* --- ✨ 按鈕現在是捲動區的第一個項目 --- */}
        {currentPage > 1 && (
          <button 
            onClick={() => onPageChange(currentPage - 1)} 
            className="btn-pagination"
            title="Previous Page"
          >
            <i className="fas fa-chevron-left"></i>
          </button>
        )}

        {/* 上傳按鈕和濾鏡列表 */}
        <div id="upload-filter-box" className="filter-swatch" onClick={onLutUploadClick}>
          <i className="fas fa-plus"></i>
          <span>Upload LUT</span>
        </div>
        {filters.map(filter => (
          <div
            key={filter.id}
            className={`filter-swatch ${selectedFilterId === filter.id ? 'selected' : ''}`}
            onClick={() => onFilterSelect(filter.id)}
          >
            <span>{filter.filter_name || filter.name}</span>
          </div>
        ))}
        
        {/* --- ✨ 按鈕現在是捲動區的最後一個項目 --- */}
        {currentPage < totalPages && (
          <button 
            onClick={() => onPageChange(currentPage + 1)} 
            className="btn-pagination"
            title="Next Page"
          >
            <i className="fas fa-chevron-right"></i>
          </button>
        )}
      </div>
    </footer>
  );
}

export default FilterBar;