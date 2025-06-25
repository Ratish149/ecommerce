function myOnOpen() {
    const ui = SpreadsheetApp.getUi();
    ui.createMenu("📤 Product Uploader")
      .addItem("⬆️ Upload Products", "uploadProducts")
      .addItem("🔄 Reload Categories", "autoFillCategories")
      .addToUi();
    autoFillCategories();  // enable for auto-fetch on open
  }
  
  function autoFillCategories() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const categoryCol = 2;     // Column B
    const subcategoryCol = 3;  // Column C
    const subsubcategoryCol = 4; // Column D
    const isPopularCol = 9;    // Column I
    const isFeaturedCol = 10;  // Column J
  
    try {
      // Fetch all dropdown data from API
      const categoryRes = UrlFetchApp.fetch("https://babies-realtor-victim-investigations.trycloudflare.com/api/categories/");
      const subcategoryRes = UrlFetchApp.fetch("https://babies-realtor-victim-investigations.trycloudflare.com/api/subcategories/");
      const subsubcategoryRes = UrlFetchApp.fetch("https://babies-realtor-victim-investigations.trycloudflare.com/api/subsubcategories/");
  
      const categories = JSON.parse(categoryRes.getContentText());
      const subcategories = JSON.parse(subcategoryRes.getContentText());
      const subsubcategories = JSON.parse(subsubcategoryRes.getContentText());
  
      // Extract category names (simple list)
      const categoryNames = categories.map(c => c.name).filter(Boolean);
      
      // Create subcategory list with parent category: "Subcategory (Category)"
      const subcategoryNames = subcategories.map(sc => {
        const parentCategory = sc.category ? sc.category.name : 'Unknown';
        return `${sc.name} (${parentCategory})`;
      }).filter(Boolean);
      
      // Create sub-subcategory list with parent subcategory: "SubSubcategory (Subcategory)"
      const subsubcategoryNames = subsubcategories.map(ssc => {
        const parentSubcategory = ssc.subcategory ? ssc.subcategory.name : 'Unknown';
        return `${ssc.name} (${parentSubcategory})`;
      }).filter(Boolean);
  
      if (categoryNames.length === 0 || subcategoryNames.length === 0 || subsubcategoryNames.length === 0) {
        SpreadsheetApp.getUi().alert("⚠️ One or more dropdown lists are empty.");
        return;
      }
  
      const startRow = 2;
      const numRows = 1000;
  
      // Set category dropdown (Column B)
      const categoryRange = sheet.getRange(startRow, categoryCol, numRows);
      const categoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(categoryNames, true)
        .setAllowInvalid(false)
        .build();
      categoryRange.setDataValidation(categoryRule);
  
      // Set subcategory dropdown (Column C)
      const subcategoryRange = sheet.getRange(startRow, subcategoryCol, numRows);
      const subcategoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(subcategoryNames, true)
        .setAllowInvalid(false)
        .build();
      subcategoryRange.setDataValidation(subcategoryRule);
  
      // Set sub-subcategory dropdown (Column D)
      const subsubcategoryRange = sheet.getRange(startRow, subsubcategoryCol, numRows);
      const subsubcategoryRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(subsubcategoryNames, true)
        .setAllowInvalid(false)
        .build();
      subsubcategoryRange.setDataValidation(subsubcategoryRule);
  
      // Set True/False dropdown for "is popular" (Column I)
      const isPopularRange = sheet.getRange(startRow, isPopularCol, numRows);
      const isPopularRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(['True', 'False'], true)
        .setAllowInvalid(false)
        .build();
      isPopularRange.setDataValidation(isPopularRule);
  
      // Set True/False dropdown for "is featured" (Column J)
      const isFeaturedRange = sheet.getRange(startRow, isFeaturedCol, numRows);
      const isFeaturedRule = SpreadsheetApp.newDataValidation()
        .requireValueInList(['True', 'False'], true)
        .setAllowInvalid(false)
        .build();
      isFeaturedRange.setDataValidation(isFeaturedRule);
  
      SpreadsheetApp.flush();
      SpreadsheetApp.getUi().alert("✅ Dropdowns for Category, Subcategory, Sub-subcategory, and True/False options applied.");
    } catch (error) {
      SpreadsheetApp.getUi().alert("❌ Failed to fetch dropdown data:\n" + error.message);
    }
  }
  
  function uploadProducts() {
    const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    const data = sheet.getDataRange().getValues();
    const headers = data[0];
  
    // Convert each row to an object
    const rows = data.slice(1).map(row => {
      let obj = {};
      headers.forEach((h, i) => {
        // Convert 'True'/'False' strings to boolean values for is_popular and is_featured
        if ((h.trim() === 'is_popular' || h.trim() === 'is_featured') && typeof row[i] === 'string') {
          obj[h.trim()] = row[i].toLowerCase() === 'true';
        } else {
          obj[h.trim()] = row[i];
        }
      });
      return obj;
    });
  
    const options = {
      method: "post",
      contentType: "application/json",
      payload: JSON.stringify({ rows }),
      muteHttpExceptions: true,
    };
  
    const url = "https://babies-realtor-victim-investigations.trycloudflare.com/api/import-products/";
  
    try {
      const res = UrlFetchApp.fetch(url, options);
      const msg = res.getContentText();
      SpreadsheetApp.getUi().alert("✅ Upload complete:\n" + msg);
    } catch (err) {
      SpreadsheetApp.getUi().alert("❌ Upload failed:\n" + err.message);
    }
  }