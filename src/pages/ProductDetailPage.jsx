import {Link, useParams} from 'react-router'
import {useState, useEffect} from 'react';



function ProductDetailPage() {
    const {id} = useParams();
    const [products, setProducts] = useState(null);
    const [Page, setPage] = useState(1);


    useEffect(() => {
        async function loadProducts() {
            const res = await fetch(`https://dummyjson.com/products/${id}`);
            const data = await res.json();
            setProducts(data);
        }
        loadProducts();
    }, [id]);

    const product = products; // Alias for cleaner code

    if (!product) return <p>Loading...</p>;
    return <>
    <Link to="/">Back to Product</Link>
    <h2>Product id: {product.title}</h2>; 
    </>
//     {/* //description, price, rating, category, stock, reviews, image */}

}

export default ProductDetailPage;