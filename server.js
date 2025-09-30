const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3000;

app.use(bodyParser.json());
app.use(express.static(path.join(__dirname)));

// API endpoint to get products
app.get('/api/products', (req, res) => {
    fs.readFile(path.join(__dirname, 'db.json'), 'utf8', (err, data) => {
        if (err) {
            console.error(err);
            return res.status(500).send('An error occurred while reading the database.');
        }
        try {
            const products = JSON.parse(data).products;
            res.json(products);
        } catch (parseErr) {
            console.error(parseErr);
            res.status(500).send('An error occurred while parsing the database.');
        }
    });
});

// API endpoint to add a new product
app.post('/api/products', (req, res) => {
    const newProduct = req.body;

    fs.readFile(path.join(__dirname, 'db.json'), 'utf8', (err, data) => {
        if (err) {
            console.error(err);
            return res.status(500).send('An error occurred while reading the database.');
        }
        try {
            const db = JSON.parse(data);
            newProduct.id = db.products.length ? Math.max(...db.products.map(p => p.id)) + 1 : 1;
            db.products.push(newProduct);

            fs.writeFile(path.join(__dirname, 'db.json'), JSON.stringify(db, null, 2), (writeErr) => {
                if (writeErr) {
                    console.error(writeErr);
                    return res.status(500).send('An error occurred while writing to the database.');
                }
                res.status(201).json({ message: 'Product added successfully!', product: newProduct });
            });
        } catch (parseErr) {
            console.error(parseErr);
            res.status(500).send('An error occurred while parsing the database.');
        }
    });
});

app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});